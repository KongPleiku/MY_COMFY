# src/components/input_bar.py
import flet as ft
from utils.data import ALL_PROMPTS

class InputBar(ft.Container):
    def __init__(self, on_send, on_cancel, on_settings_click):
        super().__init__()
        self.on_send = on_send
        self.on_cancel = on_cancel
        self.on_settings_click = on_settings_click

        # --- Controls ---
        self.prompt_field = ft.TextField(
            hint_text="Describe your image...",
            border_radius=25,
            bgcolor=ft.colors.BLACK54, 
            filled=True,
            multiline=True,
            min_lines=1, max_lines=3,
            content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
            expand=True,
            border_color=ft.colors.TRANSPARENT,
            on_change=self._on_text_change
        )

        self.suggestion_list = ft.ListView(spacing=0, padding=0)
        self.suggestion_container = ft.Container(
            content=self.suggestion_list,
            bgcolor=ft.colors.GREY_900,
            border_radius=15,
            height=0, opacity=0,
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            animate_opacity=200,
            margin=ft.margin.only(bottom=10, left=10, right=10)
        )

        # --- Layout ---
        self.bottom = 0
        self.left = 0
        self.right = 0
        self.gradient = ft.LinearGradient(
            colors=[ft.colors.TRANSPARENT, ft.colors.BLACK87],
            stops=[0.0, 0.3], begin=ft.alignment.top_center, end=ft.alignment.bottom_center
        )
        self.padding = ft.padding.only(left=10, right=10, bottom=10, top=20)
        
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.suggestion_container, 
                ft.Row(
                    controls=[
                        ft.IconButton(ft.icons.SETTINGS, icon_color=ft.colors.GREY_400, on_click=lambda e: self.on_settings_click(e)), 
                        self.prompt_field,    
                        ft.IconButton(ft.icons.CLOSE, icon_color=ft.colors.RED_400, on_click=lambda e: self.on_cancel(e)),   
                        ft.IconButton(ft.icons.ARROW_UPWARD, bgcolor=ft.colors.BLUE_700, icon_color=ft.colors.WHITE, on_click=lambda e: self.on_send(self.prompt_field.value))      
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.END
                )
            ]
        )

    def _on_text_change(self, e):
        typed = e.control.value.lower()
        if not typed.strip():
            self.hide_suggestions()
            return

        matches = [p for p in ALL_PROMPTS if typed in p.lower()]
        if not matches:
            self.hide_suggestions()
            return

        self.suggestion_list.controls = [
            ft.Container(
                content=ft.Text(m, color=ft.colors.WHITE),
                padding=15,
                data=m,
                on_click=self._use_suggestion,
                ink=True
            ) for m in matches
        ]
        
        self.suggestion_container.height = min(len(matches) * 50, 200)
        self.suggestion_container.opacity = 1
        self.suggestion_container.update()
        self.suggestion_list.update()

    def _use_suggestion(self, e):
        self.prompt_field.value = e.control.data
        self.prompt_field.update()
        self.hide_suggestions()

    def hide_suggestions(self):
        self.suggestion_container.height = 0
        self.suggestion_container.opacity = 0
        self.suggestion_container.update()

    def toggle_read_only(self, is_readonly):
        self.prompt_field.read_only = is_readonly
        self.prompt_field.update()