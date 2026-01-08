# src/components/connection_indicator.py
import flet as ft


class ConnectionIndicator(ft.Container):
    def __init__(self):
        self.status_dot = ft.Container(
            width=10,
            height=10,
            shape=ft.BoxShape.CIRCLE,
            bgcolor=ft.colors.RED_500,  # Default to red (not connected)
        )

        super().__init__(
            top=40,
            right=20,
            width=10,  # Keep the container size consistent with the dot
            height=10,
            content=self.status_dot,
            tooltip="Connection Status",
        )

    def update_status(self, is_connected: bool):
        """Updates the color of the status dot."""
        self.status_dot.bgcolor = (
            ft.colors.GREEN_500 if is_connected else ft.colors.RED_500
        )
        self.status_dot.update()
