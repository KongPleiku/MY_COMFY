# src/main.py
import flet as ft
from view import HomeView


def main(page: ft.Page):
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK

    # Initialize the main View
    home = HomeView(page)

    # Add it to the page
    page.add(home)
    home.did_mount()

    # Ensure ComfyUIClient's WebSocket connection is closed on app disconnect
    def on_disconnect(e):
        if home.gen_service:
            home.gen_service.cancel_generation()
        if home.comfy_client and home.comfy_client.is_connected():
            home.comfy_client.close_ws_connection()

    page.on_disconnect = on_disconnect


ft.app(target=main)
