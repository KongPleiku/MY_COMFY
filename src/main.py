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

ft.app(target=main)