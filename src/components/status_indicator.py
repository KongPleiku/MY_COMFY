# src/components/status_indicator.py
import flet as ft
from utils.logger import get_logger

logger = get_logger(__name__)


class StatusIndicator(ft.Container):
    def __init__(self):
        self.status_text = ft.Text(
            "Ready", size=12, weight="bold", color=ft.colors.GREEN_400
        )
        self.action_text = ft.Text("Idle", size=12, color=ft.colors.WHITE70)

        super().__init__(
            top=40,
            left=20,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.4, ft.colors.BLACK),
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Row(
                        [
                            ft.Text(
                                "ACTION:",
                                size=10,
                                color=ft.colors.GREY_400,
                                weight="bold",
                            ),
                            self.action_text,
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                "STATUS:",
                                size=10,
                                color=ft.colors.GREY_400,
                                weight="bold",
                            ),
                            self.status_text,
                        ],
                        spacing=5,
                    ),
                ],
            ),
        )
        logger.info("StatusIndicator initialized.")

    def update_status(
        self, action_text, status_text, action_color_name, status_color_name
    ):
        logger.info(f"Updating status: action='{action_text}', status='{status_text}'")
        self.action_text.value = action_text
        # Dynamically get color from flet.colors string name
        self.action_text.color = getattr(ft.colors, action_color_name, ft.colors.WHITE)
        self.status_text.value = status_text
        self.status_text.color = getattr(
            ft.colors, status_color_name, ft.colors.GREEN_400
        )
        self.update()
