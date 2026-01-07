import flet as ft

def main(page: ft.Page):
    # Android/Mobile Setup
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK 
    
    image_src = "https://picsum.photos/1080/1920"

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
        hint_text="Type your prompt...",
        border_radius=15,
        bgcolor=ft.colors.BLACK38,
        filled=True,
        multiline=True, # Make the prompt field taller
        min_lines=4,
        max_lines=4,
        text_size=14,
        content_padding=15,
    )

    # The list that will show the suggestions.
    suggestion_list = ft.Column(spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
    
    # The container for the suggestions. It animates its height and aligns its
    # content to the bottom to create the "growing upwards" effect.
    suggestion_container = ft.Container(
        content=suggestion_list,
        bgcolor=ft.colors.GREY_800,
        border_radius=10,
        padding=ft.padding.only(top=5, bottom=5),
        height=0,
        opacity=0,
        animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        animate_opacity=300,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        alignment=ft.alignment.bottom_center, # Makes the list "grow" upwards.
    )

    # --- Logic ---

    def use_suggestion(e):
        # This logic might need adjustment depending on how you want to combine hints and typed text
        current_text = prompt_field.value
        separator = ", " if current_text and not current_text.endswith(", ") else ""
        prompt_field.value = current_text + separator + e.control.data
        
        prompt_field.update()
        suggestion_container.height = 0
        suggestion_container.opacity = 0
        suggestion_container.update()

    def on_text_change(e):
        typed_text = e.control.value.lower()
        
        if not typed_text:
            suggestion_container.height = 0
            suggestion_container.opacity = 0
            suggestion_container.update()
            return

        # Filter prompts based on the last word typed after a comma
        last_word = typed_text.split(",")[-1].strip()
        if not last_word:
            suggestion_container.height = 0
            suggestion_container.opacity = 0
            suggestion_container.update()
            return

        matches = [p for p in all_prompts if last_word in p.lower()]

        if not matches:
            suggestion_container.height = 0
            suggestion_container.opacity = 0
            suggestion_container.update()
            return

        suggestion_list.controls.clear()
        for match in matches:
            suggestion_list.controls.append(
                ft.ListTile(
                    title=ft.Text(match, size=14, color=ft.colors.WHITE),
                    data=match,
                    on_click=use_suggestion,
                    border_radius=5,
                    ink=True,
                )
            )
        
        list_height = len(matches) * 45 
        if list_height > 150: list_height = 150 # Adjust max height for new layout
        
        suggestion_container.height = list_height
        suggestion_container.opacity = 1
        suggestion_container.update()
        suggestion_list.update()

    prompt_field.on_change = on_text_change

    def toggle_settings(e):
        if settings_panel.offset.y == 1:
            settings_panel.offset = ft.transform.Offset(0, 0)
            prompt_field.focus()
        else:
            settings_panel.offset = ft.transform.Offset(0, 1)
            suggestion_container.height = 0
            suggestion_container.opacity = 0
        page.update()

    # --- NEW, SIMPLIFIED LAYOUT ---

    # Section 1: The prompt area, now a Row with input on the left and hints on the right.
    prompt_section = ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            # Left side: An expanding column for the prompt field and its suggestions
            ft.Column(
                expand=True,
                controls=[
                    # The suggestion container appears first, so it will be on top
                    suggestion_container,
                    prompt_field,
                ]
            ),
            # Right side: A fixed-width container for hint words
            ft.Container(
                width=110,
                padding=ft.padding.only(left=10),
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text("Hints", weight="bold", color=ft.colors.GREY_500),
                        ft.ElevatedButton(text="1girl", on_click=use_suggestion, data="1girl", height=30),
                        ft.ElevatedButton(text="cowboy shot", on_click=use_suggestion, data="cowboy shot", height=30),
                        ft.ElevatedButton(text="masterpiece", on_click=use_suggestion, data="masterpiece", height=30),
                    ]
                )
            )
        ]
    )

    # Section 2: The scrollable settings area.
    scrollable_settings = ft.Column(
        expand=True, # This makes the column take the remaining space.
        scroll=ft.ScrollMode.HIDDEN,
        controls=[
            ft.Text("Image Settings", weight="bold", color=ft.colors.GREY_400),
            ft.Container(
                padding=10,
                content=ft.Column([
                    ft.Row([ft.Text("High Quality"), ft.Switch(value=True)], alignment="spaceBetween"),
                    ft.Row([ft.Text("Private Mode"), ft.Switch(value=False)], alignment="spaceBetween"),
                    ft.Divider(color=ft.colors.GREY_800),
                    ft.Text("Creativity Level", color=ft.colors.GREY_400),
                    ft.Slider(min=0, max=100, divisions=10, value=50),
                    ft.Container(height=20),
                    ft.Text("Model Version", weight="bold", color=ft.colors.GREY_400),
                    ft.Dropdown(
                        options=[ft.dropdown.Option("v1.0"), ft.dropdown.Option("v2.0")],
                        bgcolor=ft.colors.BLACK38, border_radius=10
                    ),
                    # Space for scrolling test
                    ft.Container(height=200),
                ])
            ),
        ]
    )

    # The main settings panel that slides up.
    settings_panel = ft.Container(
        height=page.height * 0.75, 
        bottom=0, left=0, right=0,
        bgcolor=ft.colors.GREY_900,
        border_radius=ft.border_radius.only(top_left=20, top_right=20),
        padding=20,
        offset=ft.transform.Offset(0, 1),
        animate_offset=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        clip_behavior=ft.ClipBehavior.NONE, # Allow suggestions to overflow the panel.
        # The content is now a simple Column with a clear structure.
        content=ft.Column(
            spacing=20,
            controls=[
                # 1. The drag handle and header.
                ft.Container(width=40, height=5, bgcolor=ft.colors.GREY_600, border_radius=10, alignment=ft.alignment.center),
                ft.Row([
                    ft.Text("Prompt Settings", size=20, weight="bold"), 
                    ft.IconButton(ft.icons.CLOSE, on_click=toggle_settings)
                ], alignment="spaceBetween"),
                
                # 2. The fixed prompt section.
                ft.Text("Enter Prompt", weight="bold", size=16),
                prompt_section,

                # 3. The expanding, scrollable settings section.
                scrollable_settings,
            ]
        )
    )

    page.add(
        ft.Stack(
            expand=True,
            controls=[
                ft.InteractiveViewer(
                    min_scale=1.0, max_scale=5.0,
                    boundary_margin=ft.margin.all(0),
                    content=ft.Image(src=image_src, fit=ft.ImageFit.COVER, height=page.height, width=page.width)
                ),
                ft.Container(
                    bottom=20, left=20, right=20,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.FloatingActionButton(icon=ft.icons.WIFI, bgcolor=ft.colors.BLACK54, on_click=lambda _: print("Wifi")),
                            ft.Row(spacing=10, controls=[
                                ft.FloatingActionButton(text="GEN", icon=ft.icons.AUTO_AWESOME, width=120, shape=ft.RoundedRectangleBorder(radius=30), on_click=lambda _: print("Gen")),
                                ft.FloatingActionButton(mini=True, icon=ft.icons.CLOSE, bgcolor=ft.colors.RED_900, shape=ft.CircleBorder(), on_click=lambda _: print("Cancel")),
                            ]),
                            ft.FloatingActionButton(icon=ft.icons.SETTINGS, bgcolor=ft.colors.BLACK54, on_click=toggle_settings),
                        ]
                    )
                ),
                settings_panel
            ],
        )
    )

ft.app(target=main)