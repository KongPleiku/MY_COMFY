import flet as ft

def main(page: ft.Page):
    # 1. Configuration for Fullscreen
    page.padding = 0
    page.spacing = 0
    page.bgcolor = ft.Colors.BLACK
    page.theme_mode = ft.ThemeMode.DARK

    page.vertical_alignment = ft.alignment.center
    page.horizontal_alignment = ft.alignment.center

    # 2. The Image Control
    # Replace 'assets/my_image.png' with your local file path or a URL
    img = ft.Image(
        src="https://picsum.photos/1080/1920", 
        fit=ft.ImageFit.CONTAIN, # Ensures the whole image is visible
        error_content=ft.Text("Could not load image", color="white"),
    )

    # 3. The Zoomable Viewer
    viewer = ft.InteractiveViewer(
        min_scale=0.5,      # Allow zooming out to 50%
        max_scale=5.0,      # Allow zooming in to 500%
        content=img,
        alignment=ft.alignment.center, # Keep image centered
        expand=True         # Fill the screen
    )

    # 4. Add to page
    page.add(viewer)

ft.app(target=main)