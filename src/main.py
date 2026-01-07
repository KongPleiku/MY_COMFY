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
        hint_text="Type to search prompts...",
        border_radius=15,
        bgcolor=ft.colors.BLACK38,
        filled=True,
        multiline=False,
        text_size=14,
        content_padding=15,
    )

    # The list inside the expanding container
    suggestion_list = ft.ListView(spacing=0, padding=0)
    
    # The Container ABOVE the prompt (Hidden by default via height=0)
    # This acts as the "Space" that opens up.
    suggestion_container = ft.Container(
        content=suggestion_list,
        bgcolor=ft.colors.GREY_800,
        border_radius=10,
        padding=0, # Remove padding when closed so it's perfectly hidden
        
        # Start completely collapsed
        height=0,
        opacity=0,
        
        # Animation Magic: The prompt below will slide down as this grows
        animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        animate_opacity=300,
        
        clip_behavior=ft.ClipBehavior.HARD_EDGE # Clean cut when expanding
    )

    # --- Logic ---

    def use_suggestion(e):
        prompt_field.value = e.control.data
        prompt_field.update()
        
        # Collapse the list (Prompt slides back UP)
        suggestion_container.height = 0
        suggestion_container.opacity = 0
        suggestion_container.update()

    def on_text_change(e):
        typed_text = e.control.value.lower()
        
        # Close if empty
        if not typed_text:
            suggestion_container.height = 0
            suggestion_container.opacity = 0
            suggestion_container.update()
            return

        matches = [p for p in all_prompts if typed_text in p.lower()]

        # Close if no matches
        if not matches:
            suggestion_container.height = 0
            suggestion_container.opacity = 0
            suggestion_container.update()
            return

        # Populate List
        suggestion_list.controls.clear()
        for match in matches:
            suggestion_list.controls.append(
                ft.Container(
                    content=ft.Text(match, size=14, color=ft.colors.WHITE),
                    padding=12,
                    border_radius=5,
                    data=match,
                    on_click=use_suggestion,
                    ink=True, 
                )
            )
        
        # Calculate height: 45px per item, max 200px
        list_height = len(matches) * 45 
        if list_height > 200: list_height = 200
        
        # Expand the container (Pushing the prompt down)
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
            # Reset when closing
            suggestion_container.height = 0
            suggestion_container.opacity = 0
        page.update()

    # --- Layout ---

    # The content inside the Settings Panel
    settings_content = ft.Column(
        scroll=ft.ScrollMode.HIDDEN,
        expand=True,
        controls=[
            # 1. Label on top
            ft.Text("Enter Prompt", weight="bold", size=16),
            ft.Container(height=5),

            # 2. The Dynamic Prompt Section
            # Since suggestion_container is FIRST, it appears ABOVE the prompt.
            # When it expands, it pushes the prompt (and everything below) DOWN.
            ft.Column(
                spacing=5,
                controls=[
                    suggestion_container, # The Hint List (Expands)
                    prompt_field,         # The Input Field (Slides down)
                ]
            ),
            
            # 3. The Rest of the Settings
            ft.Divider(color=ft.colors.GREY_800, height=30),
            
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

    settings_panel = ft.Container(
        height=page.height * 0.75, 
        bottom=0, left=0, right=0,
        bgcolor=ft.colors.GREY_900,
        border_radius=ft.border_radius.only(top_left=20, top_right=20),
        padding=20,
        offset=ft.transform.Offset(0, 1),
        animate_offset=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        
        content=ft.Column(
            controls=[
                # Drag Handle
                ft.Container(width=40, height=5, bgcolor=ft.colors.GREY_600, border_radius=10, alignment=ft.alignment.center),
                
                # Header
                ft.Row([
                    ft.Text("Prompt Settings", size=20, weight="bold"), 
                    ft.IconButton(ft.icons.CLOSE, on_click=toggle_settings)
                ], alignment="spaceBetween"),
                
                ft.Divider(color=ft.colors.GREY_800),

                # The Scrollable Content
                settings_content
            ]
        )
    )

    page.add(
        ft.Stack(
            controls=[
                # Background
                ft.InteractiveViewer(
                    min_scale=1.0, max_scale=5.0,
                    boundary_margin=ft.margin.all(0),
                    content=ft.Image(src=image_src, fit=ft.ImageFit.COVER, height=page.height, width=page.width)
                ),
                
                # Main UI Buttons (Bottom Bar)
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
                
                # The Slide-up Panel
                settings_panel
            ],
            expand=True
        )
    )

ft.app(target=main)