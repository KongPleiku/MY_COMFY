# src/components/input_bar.py
import flet as ft
from utils.logger import get_logger
from utils.data import ALL_PROMPTS

logger = get_logger(__name__)


class InputBar(ft.Container):
    def __init__(self, on_send, on_cancel, on_settings_click, on_change=None):
        super().__init__()
        self.on_send = on_send
        self.on_cancel = on_cancel
        self.on_settings_click = on_settings_click
        self.on_change = on_change
        logger.info("InputBar initialized.")

        # --- Controls ---
        self.prompt_field = ft.TextField(
            hint_text="Describe your image...",
            border_radius=25,
            bgcolor=ft.colors.BLACK54,
            filled=True,
            multiline=True,
            min_lines=1,
            max_lines=3,
            content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
            expand=True,
            border_color=ft.colors.TRANSPARENT,
            on_change=self._on_text_change,
        )

        self.suggestion_list = ft.ListView(spacing=0, padding=0)
        self.suggestion_container = ft.Container(
            content=self.suggestion_list,
            bgcolor=ft.colors.GREY_900,
            border_radius=15,
            height=0,
            opacity=0,
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            animate_opacity=200,
            margin=ft.margin.only(bottom=10, left=10, right=10),
        )
        self.send_button = ft.IconButton(
            ft.icons.ARROW_UPWARD,
            bgcolor=ft.colors.BLUE_700,
            icon_color=ft.colors.WHITE,
            on_click=lambda e: self._on_send_click(),
        )

        # --- Layout ---
        self.bottom = 0
        self.left = 0
        self.right = 0
        self.gradient = ft.LinearGradient(
            colors=[ft.colors.TRANSPARENT, ft.colors.BLACK87],
            stops=[0.0, 0.3],
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
        )
        self.padding = ft.padding.only(left=10, right=10, bottom=10, top=20)

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.suggestion_container,
                ft.Row(
                    controls=[
                        ft.IconButton(
                            ft.icons.SETTINGS,
                            icon_color=ft.colors.GREY_400,
                            on_click=lambda e: self.on_settings_click(e),
                        ),
                        self.prompt_field,
                        ft.IconButton(
                            ft.icons.CLOSE,
                            icon_color=ft.colors.RED_400,
                            on_click=lambda e: self.on_cancel(e),
                        ),
                        self.send_button,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
            ],
        )

    def _on_send_click(self):
        prompt = self.prompt_field.value
        logger.info(f"Send button clicked with prompt: '{prompt}'")
        self.on_send(prompt)

    def set_input_enabled(self, enabled: bool):
        """Enable or disable the send button."""
        logger.debug(f"Setting input enabled to: {enabled}")
        self.send_button.disabled = not enabled
        self.update()

    def clear_prompt(self):
        """Clears the prompt field."""
        logger.info("Clearing prompt field.")
        self.prompt_field.value = ""
        self.update()

    def set_prompt(self, value: str):
        """Sets the prompt field's value."""
        logger.debug(f"Setting prompt to: '{value}'")
        self.prompt_field.value = value
        self.update()

    def _on_text_change(self, e):
        if self.on_change:
            self.on_change()
        typed_text = e.control.value
        logger.debug(f"Text changed: '{typed_text}'")
        if not typed_text.strip():
            self.hide_suggestions()
            return

        parts = typed_text.split(",")
        current_word = parts[-1].strip().lower()

        if not current_word:
            self.hide_suggestions()
            return

        matches = [p for p in ALL_PROMPTS if p.lower().startswith(current_word)]

        if not matches:
            self.hide_suggestions()
            return

        self._update_suggestions(matches[:10])

    def _update_suggestions(self, matches):
        logger.debug(f"Updating suggestions with {len(matches)} matches.")
        self.suggestion_list.controls = [
            ft.ListTile(
                title=ft.Text(m, color=ft.colors.WHITE),
                data=m,
                on_click=self._use_suggestion,
            )
            for m in matches
        ]

        self.suggestion_container.height = min(len(matches) * 50, 200)
        self.suggestion_container.opacity = 1
        self.suggestion_container.update()
        self.suggestion_list.update()

    def _use_suggestion(self, e):
        suggestion = e.control.data
        logger.info(f"Suggestion selected: '{suggestion}'")
        current_text = self.prompt_field.value
        parts = current_text.split(",")

        # Replace the last part with the suggestion
        parts[-1] = f" {suggestion}" if len(parts) > 1 else suggestion

        self.prompt_field.value = ",".join(parts) + ", "
        self.prompt_field.update()
        self.hide_suggestions()

    def hide_suggestions(self):
        logger.debug("Hiding suggestions.")
        self.suggestion_container.height = 0
        self.suggestion_container.opacity = 0
        self.suggestion_container.update()

    def toggle_read_only(self, is_readonly):
        logger.debug(f"Toggling read-only to: {is_readonly}")
        self.prompt_field.read_only = is_readonly
        self.prompt_field.update()
