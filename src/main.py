import flet as ft
import threading # <--- FIXED: Added threading for the delay logic

def main(page: ft.Page):
    # --- Setup ---
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK 
    
    image_src = "https://picsum.photos/1080/1920"

    # --- Focus Thief ---
    focus_thief = ft.IconButton(
        icon=ft.icons.CIRCLE, opacity=0, width=0, height=0, disabled=False
    )

    # References for dynamic updates
    progress_fill_ref = ft.Ref[ft.Container]()

    # --- Data Source ---
    all_prompts = [
        "Cyberpunk city with neon lights",
        "Oil painting by Van Gogh",
        "Futuristic sci-fi portrait",
        "Peaceful sunset over the ocean",
        "Medieval castle in the mountains",
        "Cute cat wearing sunglasses",
        "Abstract geometric patterns",
        "Steampunk airship in clouds",
        "Digital art of a forest spirit",
        "Anime style character portrait",
        "Realistic landscape of Mars",
        "Underwater city with bioluminescence"
    ]

    # --- UI Elements ---
    prompt_field = ft.TextField(
        hint_text="Describe your image...",
        border_radius=25,
        bgcolor=ft.colors.BLACK54, 
        filled=True,
        multiline=True,
        min_lines=1,
        max_lines=3, 
        text_size=16,
        content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
        expand=True,
        border_color=ft.colors.TRANSPARENT,
    )

    # --- Custom Gradient Progress Bar ---
    # Placed here, but added to page AFTER bottom_input_bar in the stack
    progress_bar = ft.Container(
        bottom=85, 
        left=20, right=20, 
        height=4, 
        bgcolor=ft.colors.GREY_900, 
        border_radius=5,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        opacity=0, 
        animate_opacity=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        content=ft.Row(
            spacing=0,
            controls=[
                 ft.Container(
                    ref=progress_fill_ref, 
                    width=0, 
                    height=4,
                    border_radius=5,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.center_left,
                        end=ft.alignment.center_right,
                        colors=[ft.colors.BLUE_600, ft.colors.CYAN_400]
                    ),
                    animate=ft.animation.Animation(500, ft.AnimationCurve.EASE_OUT_CUBIC)
                )
            ]
        )
    )

    # --- Helper: Update Progress Bar ---
    def set_progress(value: float):
        available_width = page.width - 40 
        
        if value <= 0:
             progress_bar.opacity = 0 
             
             # --- FIX IS HERE ---
             # We use a Threading Timer instead of delayed_call
             def reset_width():
                 progress_fill_ref.current.width = 0
                 progress_fill_ref.current.update()
             
             # Wait 0.3s (matching the fade out animation) then reset width
             threading.Timer(0.3, reset_width).start()
             
        elif value >= 1.0:
             progress_bar.opacity = 0 
             progress_fill_ref.current.width = available_width 
        else:
             progress_bar.opacity = 1 
             progress_fill_ref.current.width = available_width * value

        progress_bar.update()
        progress_fill_ref.current.update()

    # --- Top-Left Action/Status Widget ---
    status_text = ft.Text("Ready", size=12, weight="bold", color=ft.colors.GREEN_400)
    action_text = ft.Text("Idle", size=12, color=ft.colors.WHITE70)

    status_widget = ft.Container(
        top=40, left=20,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=10,
        bgcolor=ft.colors.with_opacity(0.4, ft.colors.BLACK), 
        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR), 
        content=ft.Column(
            spacing=2,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("ACTION:", size=10, color=ft.colors.GREY_400, weight="bold"),
                        action_text
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                ft.Row(
                    controls=[
                        ft.Text("STATUS:", size=10, color=ft.colors.GREY_400, weight="bold"),
                        status_text
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                )
            ]
        )
    )

    # --- Logic: Closing Keyboard & Overlays ---
    def close_overlays(e):
        focus_thief.focus()
        prompt_field.read_only = True 
        prompt_field.update()
        
        suggestion_container.height = 0
        suggestion_container.opacity = 0
        suggestion_container.update()
        
        if settings_panel.offset.y == 0:
            settings_panel.offset = ft.transform.Offset(0, 1)
            settings_panel.update()
        
        prompt_field.read_only = False
        prompt_field.update()

    # --- Logic: Mock Generation Updates ---
    def start_generation(e):
        print("Generating: ", prompt_field.value)
        action_text.value = "Generating..."
        action_text.color = ft.colors.BLUE_200
        status_text.value = "Processing"
        status_text.color = ft.colors.ORANGE_400
        status_widget.update()
        close_overlays(None)
        
        # MOCK PROGRESS
        set_progress(0.3)

    def cancel_generation(e):
        print("Cancelled")
        action_text.value = "Idle"
        action_text.color = ft.colors.WHITE70
        status_text.value = "Ready"
        status_text.color = ft.colors.GREEN_400
        status_widget.update()
        
        set_progress(0.0)

    # --- Buttons ---
    send_button = ft.IconButton(
        icon=ft.icons.ARROW_UPWARD,
        bgcolor=ft.colors.BLUE_700,
        icon_color=ft.colors.WHITE,
        tooltip="Generate",
        on_click=start_generation
    )
    
    cancel_button = ft.IconButton(
        icon=ft.icons.CLOSE,
        icon_color=ft.colors.RED_400,
        tooltip="Cancel Generation",
        on_click=cancel_generation
    )
    
    settings_button = ft.IconButton(
        icon=ft.icons.SETTINGS,
        icon_color=ft.colors.GREY_400,
        tooltip="Settings",
        on_click=lambda e: toggle_settings(e)
    )

    # --- Suggestions System ---
    suggestion_list = ft.ListView(spacing=0, padding=0)
    
    suggestion_container = ft.Container(
        content=suggestion_list,
        bgcolor=ft.colors.GREY_900,
        border_radius=15,
        padding=0,
        height=0, 
        opacity=0,
        animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
        animate_opacity=200,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        margin=ft.margin.only(bottom=10, left=10, right=10)
    )

    def use_suggestion(e):
        prompt_field.value = e.control.data
        prompt_field.update()
        suggestion_container.height = 0
        suggestion_container.opacity = 0
        suggestion_container.update()

    def on_text_change(e):
        typed_text = e.control.value.lower()
        if not typed_text or typed_text.strip() == "":
            suggestion_container.height = 0
            suggestion_container.opacity = 0
            suggestion_container.update()
            return

        matches = [p for p in all_prompts if typed_text in p.lower()]
        if not matches:
            suggestion_container.height = 0
            suggestion_container.opacity = 0
            suggestion_container.update()
            return

        suggestion_list.controls.clear()
        for match in matches:
            suggestion_list.controls.append(
                ft.Container(
                    content=ft.Text(match, size=14, color=ft.colors.WHITE),
                    padding=15,
                    border_radius=5,
                    data=match,
                    on_click=use_suggestion,
                    ink=True,
                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE)
                )
            )
        
        list_height = len(matches) * 50 
        if list_height > 200: list_height = 200 
        suggestion_container.height = list_height
        suggestion_container.opacity = 1
        suggestion_container.update()
        suggestion_list.update()

    prompt_field.on_change = on_text_change

    # --- Settings Content ---
    sdxl_content = ft.Column(
        controls=[
            ft.Container(height=20), 
            ft.Row([ft.Text("High Quality"), ft.Switch(value=True)], alignment="spaceBetween"),
            ft.Row([ft.Text("Private Mode"), ft.Switch(value=False)], alignment="spaceBetween"),
            ft.Divider(color=ft.colors.GREY_800),
            ft.Text("Steps", color=ft.colors.GREY_400),
            ft.Slider(min=10, max=50, divisions=40, label="{value}", value=20),
            ft.Text("Guidance Scale", color=ft.colors.GREY_400),
            ft.Slider(min=0, max=20, divisions=20, label="{value}", value=7),
        ],
        scroll=ft.ScrollMode.HIDDEN
    )

    connection_content = ft.Column(
        controls=[
            ft.Container(height=20), 
            ft.TextField(label="Server URL", hint_text="http://127.0.0.1:7860", border_color=ft.colors.GREY_700),
            ft.TextField(label="API Key", password=True, can_reveal_password=True, border_color=ft.colors.GREY_700),
            ft.Container(height=10),
            ft.ElevatedButton(
                "Test Connection", 
                icon=ft.icons.WIFI, 
                bgcolor=ft.colors.BLUE_700, 
                color=ft.colors.WHITE,
                width=200
            )
        ],
        scroll=ft.ScrollMode.HIDDEN
    )

    settings_tabs = ft.Tabs(
        selected_index=0, 
        animation_duration=300,
        indicator_color=ft.colors.BLUE_400,
        label_color=ft.colors.BLUE_400,
        unselected_label_color=ft.colors.GREY_500,
        tabs=[
            ft.Tab(text="SDXL Settings", icon=ft.icons.TUNE, content=sdxl_content),
            ft.Tab(text="Connection", icon=ft.icons.LINK, content=connection_content),
        ],
        expand=True
    )

    # --- Settings Panel ---
    def toggle_settings(e):
        if settings_panel.offset.y == 0:
            close_overlays(None)
        else:
            settings_tabs.selected_index = 0
            settings_tabs.update()
            settings_panel.offset = ft.transform.Offset(0, 0)
            focus_thief.focus() 
            page.update()

    settings_panel = ft.Container(
        height=page.height * 0.6,
        bottom=0, left=0, right=0,
        bgcolor=ft.colors.GREY_900,
        border_radius=ft.border_radius.only(top_left=20, top_right=20),
        padding=20,
        offset=ft.transform.Offset(0, 1), 
        animate_offset=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        content=ft.Column([
            ft.Container(width=40, height=5, bgcolor=ft.colors.GREY_600, border_radius=10, alignment=ft.alignment.center),
            ft.Row([
                ft.Text("Settings", size=20, weight="bold"), 
                ft.IconButton(ft.icons.CLOSE, on_click=close_overlays)
            ], alignment="spaceBetween"),
            ft.Divider(color=ft.colors.GREY_800),
            settings_tabs
        ])
    )

    # --- The Bottom Prompt Bar ---
    bottom_input_bar = ft.Container(
        bottom=0, left=0, right=0,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.colors.TRANSPARENT, ft.colors.BLACK87],
            stops=[0.0, 0.3]
        ),
        padding=ft.padding.only(left=10, right=10, bottom=10, top=20),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                suggestion_container, 
                ft.Row(
                    controls=[
                        settings_button, 
                        prompt_field,    
                        cancel_button,   
                        send_button      
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.END
                )
            ]
        )
    )

    # --- Main Build ---
    page.add(
        ft.Stack(
            controls=[
                # 1. Background Viewer (Bottom Layer)
                ft.InteractiveViewer(
                    min_scale=1.0, max_scale=5.0, boundary_margin=ft.margin.all(0),
                    on_interaction_start=lambda e: close_overlays(e),
                    content=ft.Image(src=image_src, fit=ft.ImageFit.COVER, height=page.height, width=page.width)
                ),
                
                # 2. Status Widget
                status_widget,

                # 3. Bottom Prompt Bar (Background gradient)
                bottom_input_bar,
                
                # 4. Progress Bar (Top Layer!)
                progress_bar,
                
                # 5. Settings Panel
                settings_panel,

                # 6. Focus Thief
                focus_thief
            ],
            expand=True
        )
    )

ft.app(target=main)