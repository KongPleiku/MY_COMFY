# src/views/home_view.py
import flet as ft
import threading
from utils.data import IMAGE_SRC
from components.status_indicator import StatusIndicator
from components.setting_panel import SettingsPanel
from components.input_bar import InputBar
from services.generation_services import GenerationService

class HomeView(ft.Stack):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True

        # --- 1. Initialize Service ---
        # We pass methods from this view to the service so it can trigger updates
        self.gen_service = GenerationService(
            on_progress_update=self.update_progress_bar,
            on_status_update=self.update_status_widget
        )

        # --- 2. Initialize Components ---
        self.status_widget = StatusIndicator()
        
        self.input_bar = InputBar(
            on_send=self.gen_service.start_generation,
            on_cancel=lambda e: self.gen_service.cancel_generation(),
            on_settings_click=self.toggle_settings
        )

        self.settings_sheet = SettingsPanel(
            page_height=page.height,
            on_close=lambda: self.close_overlays(None)
        )

        # Focus Thief (for hiding keyboard)
        self.focus_thief = ft.IconButton(icon=ft.icons.CIRCLE, opacity=0, width=0, height=0)

        # Progress Bar References (Kept local as it's purely visual)
        self.progress_fill_ref = ft.Ref[ft.Container]()
        self.progress_container = self._build_progress_bar()

        # --- 3. Build Layout ---
        self.controls = [
            # Background
            ft.InteractiveViewer(
                min_scale=1.0, max_scale=5.0,
                on_interaction_start=self.close_overlays,
                content=ft.Image(src=IMAGE_SRC, fit=ft.ImageFit.COVER, height=page.height, width=page.width)
            ),
            # UI Components
            self.status_widget,
            self.input_bar,
            self.progress_container,
            self.settings_sheet,
            self.focus_thief
        ]

    def _build_progress_bar(self):
        return ft.Container(
            bottom=85, left=20, right=20, height=4,
            bgcolor=ft.colors.GREY_900, border_radius=5,
            opacity=0, animate_opacity=300,
            content=ft.Row([
                ft.Container(
                    ref=self.progress_fill_ref, width=0, height=4, border_radius=5,
                    gradient=ft.LinearGradient(colors=[ft.colors.BLUE_600, ft.colors.CYAN_400]),
                    animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC)
                )
            ])
        )

    # --- Callbacks triggered by Service ---

    def update_status_widget(self, action, status, ac_color, st_color):
        self.status_widget.update_status(action, status, ac_color, st_color)
        if action == "Generating...":
            self.close_overlays(None)

    def update_progress_bar(self, value: float):
        # Calculate width based on current page size
        available_width = self.page.width - 40
        
        if value <= 0:
            # Hide
            self.progress_container.opacity = 0
            # Reset width after fade out (Threading logic preserved)
            threading.Timer(0.3, lambda: self._reset_fill()).start()
        elif value >= 1.0:
            # Done
            self.progress_container.opacity = 0
            self.progress_fill_ref.current.width = available_width
        else:
            # Update
            self.progress_container.opacity = 1
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
            
        # Trick to close keyboard on mobile by toggling read_only
        self.input_bar.toggle_read_only(True)
        self.input_bar.toggle_read_only(False)

    def toggle_settings(self, e):
        if self.settings_sheet.offset.y == 0:
            self.close_overlays(None)
        else:
            self.settings_sheet.open()