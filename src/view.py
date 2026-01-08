# src/views/home_view.py
import flet as ft
import threading
from utils.data import IMAGE_SRC
from components.status_indicator import StatusIndicator
from components.connection_indicator import ConnectionIndicator
from components.setting_panel import SettingsPanel
from components.input_bar import InputBar
from services.generation_services import (
    GenerationService,
)
from services.client import ComfyUIClient
from services.config_service import ConfigService
import base64
from PIL import Image
import io

class HomeView(ft.Stack):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self._is_connecting = False

        self.current_height = 0
        self.current_width = 0

        # --- 1. Initialize Services and Clients ---
        self.config_service = ConfigService()
        self.comfy_client = ComfyUIClient()  # ComfyUIClient instance is now sustained
        self.gen_service = GenerationService(
            comfy_client=self.comfy_client,
            on_progress_update=self.update_progress_bar,
            on_status_update=self.update_status_widget,
            on_image_update=self.update_image,
            on_preview_update=self.update_preview,
        )

        # --- 2. Initialize Components ---
        self.status_widget = StatusIndicator()
        self.connection_indicator = ConnectionIndicator()

        self.input_bar = InputBar(
            on_send=self.start_generation_from_input,
            on_cancel=lambda e: self.gen_service.cancel_generation(),
            on_settings_click=self.toggle_settings,
            on_change=self._save_config,
        )

        self.settings_sheet = SettingsPanel(
            page_height=page.height,
            on_close=lambda: self.close_overlays(None),
            on_connect_click=self.handle_connect_click,
            on_change=self._save_config,
        )

        self.background_image = ft.Image(
            src=IMAGE_SRC,
            fit=ft.ImageFit.FIT_WIDTH,
            height=self.page.height,
            width=self.page.width,
        )

        # Focus Thief (for hiding keyboard)
        self.focus_thief = ft.IconButton(
            icon=ft.icons.CIRCLE, opacity=0, width=0, height=0
        )

        # Progress Bar References
        self.progress_fill_ref = ft.Ref[ft.Container]()
        self.progress_container = self._build_progress_bar()

        # --- 3. Build Layout ---
        self.controls = [
            ft.InteractiveViewer(
                min_scale=1.0,
                max_scale=5.0,
                on_interaction_start=self.close_overlays,
                content=self.background_image,
            ),
            self.status_widget,
            self.connection_indicator,
            self.input_bar,
            self.progress_container,
            self.settings_sheet,
            self.focus_thief,
        ]

    def did_mount(self):
        self._load_config_and_connect()

    def _load_config_and_connect(self):
        config = self.config_service.load_config()
        if config:
            gen_settings = config.get("generation_setting")
            face_detailer_setting = config.get("face_detailer_setting")
            prompt = config.get("prompt")
            connection_url = config.get("connection_url")

            if gen_settings:
                self.settings_sheet.set_settings(gen_settings, face_detailer_setting)
            if prompt:
                self.input_bar.set_prompt(prompt)
            if connection_url:
                self.handle_connect_click(connection_url)

    def _save_config(self, e=None):
        gen_settings, face_detailer_setting = self.settings_sheet.get_settings()
        prompt = self.input_bar.prompt_field.value
        config = {
            "generation_setting": gen_settings,
            "face_detailer_setting": face_detailer_setting,
            "prompt": prompt,
            "connection_url": self.comfy_client.api_url,
        }
        self.config_service.save_config(config)

    def start_generation_from_input(self, prompt: str):
        """
        Called by the InputBar's send button.
        Creates settings objects and starts the generation.
        """
        self._save_config()
        # For now, we'll create default settings and just change the prompt.
        # Later, these can be populated from the UI.
        generation_setting, face_detailer_setting = self.settings_sheet.get_settings()
        generation_setting["positive_prompt"] = prompt

        self.gen_service.start_generation(
            setting=generation_setting,
            face_detailer_setting=face_detailer_setting,
        )

    def handle_connect_click(self, url: str):
        """Starts the connection process in a background thread."""
        if self._is_connecting:
            return
        self._is_connecting = True
        print(f"Attempting to connect to {url}...")
        thread = threading.Thread(target=self._connect_worker, args=(url,))
        thread.start()

    def _connect_worker(self, url: str):
        """Connects to ComfyUI and updates status (runs in a thread)."""
        try:
            self.comfy_client.set_api_url(url)  # Update the sustained client's URL
            is_connected = (
                self.comfy_client.connect()
            )  # Connect using the sustained client

            if is_connected:
                print("Successfully connected to ComfyUI.")
                self._save_config()
            else:
                print("Failed to connect to ComfyUI.")

            # Update the UI on the main thread
            self.connection_indicator.update_status(is_connected)
            self.page.update()  # Ensure UI updates are reflected
        finally:
            self._is_connecting = False

    def update_image(self, image_b64: str):
        # Inside the update_image(self, image_b64: str) method:
         # 1. Decode the base64 string to binary
        image_bytes = base64.b64decode(image_b64)
     
         # 2. Open the image using Pillow
        img = Image.open(io.BytesIO(image_bytes))
     
         # 3. Check if rotation is needed and rotate the image object
        config = self.config_service.load_config()

        current_height = config["generation_setting"]["height"]
        current_width = config["generation_setting"]["width"]

        if current_height < current_width:
            img = img.rotate(-90, expand=True)
   
        # 4. Save the potentially rotated image to a new byte buffer
        output_buffer = io.BytesIO()
        img.save(output_buffer, format="PNG")
   
        # 5. Get the new base64 string
        new_image_b64 = base64.b64encode(output_buffer.getvalue()).decode("utf-8")
   
        # 6. Update the UI control with the new image and its correct dimensions
        self.background_image.rotate = None # Ensure no framework rotation is applied
        self.background_image.src_base64 = new_image_b64
        self.background_image.update()

    def update_preview(self, image_b64: str):
        # Inside the update_image(self, image_b64: str) method:
         # 1. Decode the base64 string to binary
        image_bytes = base64.b64decode(image_b64)
     
         # 2. Open the image using Pillow
        img = Image.open(io.BytesIO(image_bytes))
     
         # 3. Check if rotation is needed and rotate the image object
        config = self.config_service.load_config()

        current_height = config["generation_setting"]["height"]
        current_width = config["generation_setting"]["width"]

        if current_height < current_width:
            img = img.rotate(-90, expand=True)
   
        # 4. Save the potentially rotated image to a new byte buffer
        output_buffer = io.BytesIO()
        img.save(output_buffer, format="PNG")
   
        # 5. Get the new base64 string
        new_image_b64 = base64.b64encode(output_buffer.getvalue()).decode("utf-8")
   
        # 6. Update the UI control with the new image and its correct dimensions
        self.background_image.rotate = None # Ensure no framework rotation is applied
        self.background_image.src_base64 = new_image_b64
        self.background_image.update()

    def _build_progress_bar(self):
        return ft.Container(
            bottom=0,
            left=0,
            right=0,
            height=4,
            bgcolor=ft.colors.GREY_900,
            border_radius=5,
            opacity=0,
            animate_opacity=300,
            content=ft.Row(
                [
                    ft.Container(
                        ref=self.progress_fill_ref,
                        width=0,
                        height=4,
                        border_radius=5,
                        gradient=ft.LinearGradient(
                            colors=[ft.colors.BLUE_600, ft.colors.CYAN_400]
                        ),
                        animate=ft.animation.Animation(
                            500, ft.AnimationCurve.EASE_OUT_CUBIC
                        ),
                    )
                ]
            ),
        )

    # --- Callbacks triggered by Service ---

    def update_status_widget(self, action, status, ac_color, st_color):
        self.status_widget.update_status(action, status, ac_color, st_color)

        is_generating = action in ["Queuing...", "Generating...", "Downloading..."]
        self.input_bar.set_input_enabled(not is_generating)

        if action == "Generating...":
            self.close_overlays(None)
        elif action == "Finished":
            # Optionally clear prompt on finish
            self.input_bar.clear_prompt()

    def update_progress_bar(self, value: float):
        available_width = self.page.width

        if value <= 0:
            self.progress_container.opacity = 0
            threading.Timer(0.3, lambda: self._reset_fill()).start()
        elif value >= 1.0:
            self.progress_container.opacity = 0
            if self.progress_fill_ref.current:
                self.progress_fill_ref.current.width = available_width
        else:
            self.progress_container.opacity = 1
            if self.progress_fill_ref.current:
                self.progress_fill_ref.current.width = available_width * value

        self.progress_container.update()
        if self.progress_fill_ref.current:
            self.progress_fill_ref.current.update()

    def _reset_fill(self):
        if self.progress_fill_ref.current:
            self.progress_fill_ref.current.width = 0
            self.progress_fill_ref.current.update()

    def close_overlays(self, e):
        self.focus_thief.focus()
        self.input_bar.hide_suggestions()

        if self.settings_sheet.offset.y == 0:
            self.settings_sheet.offset = ft.transform.Offset(0, 1)
            self.settings_sheet.update()

        self.input_bar.toggle_read_only(True)
        self.input_bar.toggle_read_only(False)

    def toggle_settings(self, e):
        if self.settings_sheet.offset.y == 0:
            self.close_overlays(None)
        else:
            self.settings_sheet.open()
