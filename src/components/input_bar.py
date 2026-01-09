import flet as ft
from utils.logger import get_logger
from utils.data import ALL_PROMPTS
import re

logger = get_logger(__name__)

class InputBar(ft.Container):
    def __init__(self, on_send, on_cancel, on_settings_click, on_change=None):
        super().__init__()
        self.on_send = on_send
        self.on_cancel = on_cancel
        self.on_settings_click = on_settings_click
        self.on_change = on_change
        
        # State tracking
        self.cursor_position = 0
        self.last_value = ""
        
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
            expand=True, # This will now have more room to expand
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

        # 1. Define the Cancel button explicitly
        self.cancel_button = ft.IconButton(
            ft.icons.CLOSE,
            icon_color=ft.colors.RED_400,
            on_click=lambda e: self.on_cancel(e),
        )

        # 2. Define the Send button
        self.send_button = ft.IconButton(
            ft.icons.ARROW_UPWARD,
            bgcolor=ft.colors.BLUE_700,
            icon_color=ft.colors.WHITE,
            on_click=lambda e: self._on_send_click(),
        )

        # 3. Create a Column to stack them vertically
        self.button_stack = ft.Column(
            controls=[
                self.cancel_button,
                self.send_button
            ],
            spacing=5, # Small gap between the two buttons
            alignment=ft.MainAxisAlignment.END,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
                        # 4. Replace the individual buttons with the stack
                        self.button_stack, 
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
            ],
        )

    def _on_send_click(self):
        prompt = self.prompt_field.value
        logger.info(f"Send button clicked with prompt: '{prompt}'")
        self.on_send(prompt)
        # Reset tracker on send
        self.last_value = "" 

    def set_input_enabled(self, enabled: bool):
        self.send_button.disabled = not enabled
        self.update()

    def clear_prompt(self):
        self.prompt_field.value = ""
        self.last_value = ""
        self.update()

    def set_prompt(self, value: str):
        self.prompt_field.value = value
        self.last_value = value
        self.update()

    # --- INTELLIGENT SUGGESTION LOGIC ---

    def _calculate_cursor_position(self, current_text):
        """
        Since Flet 0.25.2 lacks selection property, we infer the cursor position
        by comparing the old text (self.last_value) with the new text.
        """
        if not self.last_value:
            return len(current_text)
        
        # 1. Find the length of the common prefix (where text is identical)
        common_len = 0
        min_len = min(len(current_text), len(self.last_value))
        while common_len < min_len and current_text[common_len] == self.last_value[common_len]:
            common_len += 1
            
        # 2. Estimate cursor based on change type
        if len(current_text) >= len(self.last_value):
            # Insertion (Typing): Cursor is at end of inserted segment
            inserted_count = len(current_text) - len(self.last_value)
            return common_len + inserted_count
        else:
            # Deletion (Backspace): Cursor is at the point of divergence
            return common_len

    def _get_word_boundary(self):
        text = self.prompt_field.value
        cursor = self.cursor_position

        if not text:
            return None, None, None

        # Look strictly BEHIND the calculated cursor
        text_before_cursor = text[:cursor]

        # Regex: Find the continuous word characters touching the end of the string
        match = re.search(r"[\w-]+$", text_before_cursor)

        if not match:
            return None, None, None

        # The start index in the FULL text
        start = match.start()
        # The end index is effectively our cursor
        end = cursor
        current_word = match.group(0)

        return start, end, current_word

    def _on_text_change(self, e):
        current_text = e.control.value
        
        # 1. Calculate cursor position before updating last_value
        self.cursor_position = self._calculate_cursor_position(current_text)
        
        # 2. Update last_value for the next event
        self.last_value = current_text

        if self.on_change:
            self.on_change()
            
        self._trigger_suggestions()

    def _trigger_suggestions(self):
        start, end, current_word = self._get_word_boundary()

        if not current_word:
            self.hide_suggestions()
            return

        # Smart Filtering
        matches = [p for p in ALL_PROMPTS if p.lower().startswith(current_word.lower())]

        # Exact match check (if user finished typing the word, hide menu)
        if len(matches) == 1 and matches[0].lower() == current_word.lower():
            self.hide_suggestions()
            return

        if not matches:
            self.hide_suggestions()
            return

        self._update_suggestions(matches[:10])

    def _update_suggestions(self, matches):
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
        text = self.prompt_field.value
        
        # Recalculate boundary based on current cursor
        start, end, current_word = self._get_word_boundary()

        if start is None:
            return

        # Split text into 3 parts: Before word, The word (removed), After cursor
        text_before = text[:start]
        text_after = text[end:]

        # Create new prompt
        new_text = f"{text_before}{suggestion} {text_after}"

        self.prompt_field.value = new_text
        self.last_value = new_text  # CRITICAL: Sync last_value so next type works
        self.prompt_field.update()
        self.prompt_field.focus()
        self.hide_suggestions()

    def hide_suggestions(self):
        self.suggestion_container.height = 0
        self.suggestion_container.opacity = 0
        self.suggestion_container.update()
    
    def toggle_read_only(self, is_readonly):
        logger.debug(f"Toggling read-only to: {is_readonly}")
        self.prompt_field.read_only = is_readonly
        self.prompt_field.update()