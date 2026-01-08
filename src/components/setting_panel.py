# src/components/setting_panel.py
import flet as ft
import random
from services.generation_services import GenerationSetting, FaceDetailerSetting


class SettingsPanel(ft.Container):
    def __init__(self, page_height, on_close, on_connect_click, on_change=None):
        super().__init__()
        self.on_close_callback = on_close
        self.on_connect_click = on_connect_click
        self.on_change = on_change
        self._is_setting_from_config = False

        self.url_field = ft.TextField(
            label="Server URL",
            hint_text="http://127.0.0.1:8188",
            value="http://n3.ckey.vn:1609",
            on_change=self._on_setting_change,
        )
        # --- Controls for GenerationSetting ---
        self.model_field = ft.TextField(
            label="Model", value="WAI_ANI_Q8_0.gguf", on_change=self._on_setting_change
        )
        self.seed_field = ft.TextField(
            label="Seed", value="1", width=150, on_change=self._on_setting_change
        )
        self.width_field = ft.TextField(
            label="Width", value="1024", expand=True, on_change=self._on_setting_change
        )
        self.height_field = ft.TextField(
            label="Height", value="1024", expand=True, on_change=self._on_setting_change
        )

        self.fixed_seed_checkbox = ft.Checkbox(
            label="Fixed", value=True, on_change=self._on_setting_change
        )
        self.randomize_button = ft.IconButton(
            icon=ft.icons.CASINO_OUTLINED,
            tooltip="Randomize Seed",
            on_click=self._randomize_seed,
        )

        self.steps_slider = ft.Slider(
            min=1,
            max=100,
            divisions=99,
            label="Steps: {value}",
            value=20,
            on_change=self._on_setting_change,
        )
        self.cfg_slider = ft.Slider(
            min=1,
            max=20,
            divisions=19,
            label="CFG: {value}",
            value=4,
            on_change=self._on_setting_change,
        )

        self.sampler_dropdown = ft.Dropdown(
            label="Sampler",
            value="euler_ancestral",
            options=[
                ft.dropdown.Option("euler_ancestral"),
                ft.dropdown.Option("euler"),
                ft.dropdown.Option("dpm++_2m_karras"),
            ],
            expand=True,
            on_change=self._on_setting_change,
        )
        self.scheduler_dropdown = ft.Dropdown(
            label="Scheduler",
            value="sgm_uniform",
            options=[
                ft.dropdown.Option("sgm_uniform"),
                ft.dropdown.Option("normal"),
                ft.dropdown.Option("karras"),
                ft.dropdown.Option("simple"),
            ],
            expand=True,
            on_change=self._on_setting_change,
        )

        # --- Controls for FaceDetailer ---
        self.face_detailer_switch = ft.Switch(
            value=False, on_change=self.toggle_face_detailer_settings
        )

        self.fd_steps_slider = ft.Slider(
            min=1,
            max=50,
            divisions=49,
            label="Face Detailer Steps: {value}",
            value=20,
            on_change=self._on_setting_change,
        )
        self.fd_cfg_slider = ft.Slider(
            min=1,
            max=20,
            divisions=19,
            label="Face Detailer CFG: {value}",
            value=10,
            on_change=self._on_setting_change,
        )
        self.fd_sampler_dropdown = ft.Dropdown(
            label="Sampler",
            value="euler_ancestral",
            options=[
                ft.dropdown.Option("euler_ancestral"),
                ft.dropdown.Option("euler"),
                ft.dropdown.Option("dpm++_2m_karras"),
            ],
            expand=True,
            on_change=self._on_setting_change,
        )
        self.fd_scheduler_dropdown = ft.Dropdown(
            label="Scheduler",
            value="sgm_uniform",
            options=[
                ft.dropdown.Option("sgm_uniform"),
                ft.dropdown.Option("normal"),
                ft.dropdown.Option("karras"),
                ft.dropdown.Option("simple"),
            ],
            expand=True,
            on_change=self._on_setting_change,
        )
        self.fd_denoise_slider = ft.Slider(
            min=0.1,
            max=1.0,
            divisions=9,
            label="Denoise: {value}",
            value=0.4,
            on_change=self._on_setting_change,
        )
        self.fd_bbox_threshold_slider = ft.Slider(
            min=0.1,
            max=1.0,
            divisions=9,
            label="BBox Threshold: {value}",
            value=0.5,
            on_change=self._on_setting_change,
        )
        self.fd_bbox_crop_factor_slider = ft.Slider(
            min=1.0,
            max=4.0,
            divisions=30,
            label="BBox Crop Factor: {value}",
            value=2,
            on_change=self._on_setting_change,
        )
        self.face_detailer_settings_container = ft.Column(
            controls=[
                self.fd_steps_slider,
                self.fd_cfg_slider,
                ft.Row([self.fd_sampler_dropdown, self.fd_scheduler_dropdown]),
                self.fd_denoise_slider,
                self.fd_bbox_threshold_slider,
                self.fd_bbox_crop_factor_slider,
            ],
            visible=False,
            animate_opacity=300,
        )

        self.sdxl_tab = ft.Column(
            controls=[
                ft.Container(height=10),
                self.model_field,
                ft.Row(
                    [
                        self.seed_field,
                        self.fixed_seed_checkbox,
                        self.randomize_button,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Row([self.width_field, self.height_field]),
                ft.Text("Steps"),
                self.steps_slider,
                ft.Text("CFG Scale"),
                self.cfg_slider,
                ft.Row([self.sampler_dropdown, self.scheduler_dropdown]),
                ft.Divider(height=10, color="transparent"),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Text("Use Face Detailer"),
                        self.face_detailer_switch,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self.face_detailer_settings_container,
            ],
            scroll=ft.ScrollMode.AUTO,
        )
        self.conn_tab = ft.Column(
            controls=[
                ft.Container(height=20),
                self.url_field,
                ft.ElevatedButton(
                    "Test Connection",
                    icon=ft.icons.WIFI,
                    on_click=lambda e: self.on_connect_click(self.url_field.value),
                ),
            ]
        )

        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="SDXL Settings", icon=ft.icons.TUNE, content=self.sdxl_tab),
                ft.Tab(text="Connection", icon=ft.icons.LINK, content=self.conn_tab),
            ],
            expand=True,
        )

        # --- Container Config ---
        self.height = page_height * 0.8
        self.bottom = 0
        self.left = 0
        self.right = 0
        self.bgcolor = ft.colors.with_opacity(0.95, ft.colors.GREY_900)
        self.border_radius = ft.border_radius.only(top_left=20, top_right=20)
        self.padding = 20
        self.offset = ft.transform.Offset(0, 1)  # Hidden
        self.animate_offset = ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)

        self.content = ft.Column(
            [
                ft.Container(
                    width=40,
                    height=5,
                    bgcolor=ft.colors.GREY_600,
                    border_radius=10,
                    alignment=ft.alignment.center,
                    on_click=lambda e: self.close(),
                ),
                ft.Row(
                    [
                        ft.Text("Settings", size=20, weight="bold"),
                        ft.IconButton(ft.icons.CLOSE, on_click=lambda e: self.close()),
                    ],
                    alignment="spaceBetween",
                ),
                ft.Divider(color=ft.colors.GREY_800),
                self.tabs,
            ],
            expand=True,
        )

    def open(self):
        self.tabs.selected_index = 0
        self.offset = ft.transform.Offset(0, 0)
        self.update()

    def close(self):
        self.on_close_callback()

    def toggle_face_detailer_settings(self, e):
        self.face_detailer_settings_container.visible = e.control.value
        self.face_detailer_settings_container.opacity = 1 if e.control.value else 0
        self.update()

    def _on_setting_change(self, e):
        if not self._is_setting_from_config and self.on_change:
            self.on_change()

    def _randomize_seed(self, e):
        self.seed_field.value = str(random.randint(0, 2**32 - 1))
        self.update()
        if self.on_change:
            self.on_change()

    def is_seed_fixed(self):
        return self.fixed_seed_checkbox.value
    
    def _clamp(self, value, min_val, max_val):
        return max(min_val, min(value, max_val))

    def set_settings(
        self,
        gen_settings: GenerationSetting,
        face_detailer_setting: FaceDetailerSetting | None,
    ):
        self._is_setting_from_config = True
        try:
            # General settings
            self.model_field.value = gen_settings.get("model", "WAI_ANI_Q8_0.gguf")
            self.seed_field.value = str(gen_settings.get("seed", "1"))
            self.width_field.value = str(gen_settings.get("width", "1024"))
            self.height_field.value = str(gen_settings.get("height", "1024"))
            self.sampler_dropdown.value = gen_settings.get("sampler_name", "euler_ancestral")
            self.scheduler_dropdown.value = gen_settings.get("scheduler", "sgm_uniform")

            # Clamp slider values
            self.steps_slider.value = self._clamp(int(gen_settings.get("steps", 20)), self.steps_slider.min, self.steps_slider.max)
            self.cfg_slider.value = self._clamp(int(gen_settings.get("cfg", 4)), self.cfg_slider.min, self.cfg_slider.max)

            # Face detailer switch
            use_face_detailer = gen_settings.get("Face_detailer_switch", 1) == 2
            self.face_detailer_switch.value = use_face_detailer
            self.face_detailer_settings_container.visible = use_face_detailer
            self.face_detailer_settings_container.opacity = 1 if use_face_detailer else 0

            # Face detailer settings
            if face_detailer_setting:
                self.fd_sampler_dropdown.value = face_detailer_setting.get("sampler_name", "euler_ancestral")
                self.fd_scheduler_dropdown.value = face_detailer_setting.get("scheduler", "sgm_uniform")

                # Clamp face detailer slider values
                self.fd_steps_slider.value = self._clamp(int(face_detailer_setting.get("steps", 20)), self.fd_steps_slider.min, self.fd_steps_slider.max)
                self.fd_cfg_slider.value = self._clamp(int(face_detailer_setting.get("cfg", 10)), self.fd_cfg_slider.min, self.fd_cfg_slider.max)
                self.fd_denoise_slider.value = self._clamp(float(face_detailer_setting.get("denoise", 0.4)), self.fd_denoise_slider.min, self.fd_denoise_slider.max)
                self.fd_bbox_threshold_slider.value = self._clamp(float(face_detailer_setting.get("bbox_threshold", 0.5)), self.fd_bbox_threshold_slider.min, self.fd_bbox_threshold_slider.max)
                self.fd_bbox_crop_factor_slider.value = self._clamp(float(face_detailer_setting.get("bbox_crop_factor", 2)), self.fd_bbox_crop_factor_slider.min, self.fd_bbox_crop_factor_slider.max)
            
            self.update()
        finally:
            self._is_setting_from_config = False

    def get_settings(self) -> tuple[GenerationSetting, FaceDetailerSetting | None]:
        seed = int(self.seed_field.value)
        if not self.fixed_seed_checkbox.value:
            seed = random.randint(0, 2**32 - 1)
            self.seed_field.value = str(seed)
            self.update()

        gen_settings: GenerationSetting = {
            "model": self.model_field.value,
            "positive_prompt": "",  # This will be set in the view
            "seed": seed,
            "steps": int(self.steps_slider.value),
            "cfg": int(self.cfg_slider.value),
            "sampler_name": self.sampler_dropdown.value,
            "scheduler": self.scheduler_dropdown.value,
            "width": int(self.width_field.value),
            "height": int(self.height_field.value),
            "Face_detailer_switch": 2 if self.face_detailer_switch.value else 1,
        }

        face_detailer_settings: FaceDetailerSetting | None = None
        if self.face_detailer_switch.value:
            face_detailer_settings = {
                "steps": int(self.fd_steps_slider.value),
                "cfg": int(self.fd_cfg_slider.value),
                "sampler_name": self.fd_sampler_dropdown.value,
                "scheduler": self.fd_scheduler_dropdown.value,
                "denoise": float(self.fd_denoise_slider.value),
                "bbox_threshold": float(self.fd_bbox_threshold_slider.value),
                "bbox_crop_factor": float(self.fd_bbox_crop_factor_slider.value),
            }

        return gen_settings, face_detailer_settings
