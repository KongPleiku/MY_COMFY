import flet as ft

def main(page: ft.Page):
    # Android specific setup
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
        expand=True,
        content_padding=15
    )

    # The list inside the floating container
    suggestion_list = ft.ListView(spacing=0, padding=0)
    
    # The Container that holds the list (Hidden by default)
    suggestion_container = ft.Container(
        content=suggestion_list,
        bgcolor=ft.colors.GREY_800,
        border_radius=10,
        padding=5,
        visible=False,
        
        # --- POSITIONING MAGIC FOR "GROW UP" EFFECT ---
        # Instead of 'top', we use 'bottom'.
        # The input is at bottom=0. The input is approx 50-60px tall.
        # So we start this list at bottom=60.
        bottom=60, 
        left=0, 
        right=0,
        
        shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK),
    )

    # --- Logic ---

    def use_suggestion(e):
        prompt_field.value = e.control.data
        prompt_field.update()
        suggestion_container.visible = False
        suggestion_container.update()

    def on_text_change(e):
        typed_text = e.control.value.lower()
        
        if not typed_text:
            suggestion_container.visible = False
            suggestion_container.update()
            return

        matches = [p for p in all_prompts if typed_text in p.lower()]

        if not matches:
            suggestion_container.visible = False
            suggestion_container.update()
            return

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
        
        suggestion_container.height = list_height
        suggestion_container.visible = True
        
        suggestion_container.update()
        suggestion_list.update()

    prompt_field.on_change = on_text_change

    def toggle_settings(e):
        if settings_panel.offset.y == 1:
            settings_panel.offset = ft.transform.Offset(0, 0)
            prompt_field.focus()
        else:
            settings_panel.offset = ft.transform.Offset(0, 1)
            suggestion_container.visible = False
        page.update()

    # --- Layout ---

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
                # Header
                ft.Container(width=40, height=5, bgcolor=ft.colors.GREY_600, border_radius=10, alignment=ft.alignment.center),
                ft.Row([ft.Text("Prompt Settings", size=20, weight="bold"), ft.IconButton(ft.icons.CLOSE, on_click=toggle_settings)], alignment="spaceBetween"),
                ft.Divider(color=ft.colors.GREY_800),

                # --- STACK FOR "GROW UP" UI ---
                ft.Stack(
                    height=300, # Reserve enough height for the list to grow UP into
                    controls=[
                        # Layer 1: The Suggestions (Now anchored to BOTTOM, sitting on top of input)
                        suggestion_container,

                        # Layer 2: The Input Field (Anchored to BOTTOM)
                        ft.Container(
                            height=50, 
                            bottom=0, left=0, right=0,
                            content=ft.Row([prompt_field])
                        ),
                    ]
                )
            ]
        )
    )

    page.add(
        ft.Stack(
            controls=[
                ft.InteractiveViewer(
                    min_scale=1.0, max_scale=5.0,
                    boundary_margin=ft.margin.all(0),
                    content=ft.Image(src=image_src, fit=ft.ImageFit.COVER, height=page.height, width=page.width)
                ),
                ft.Text("Status: Connected", size=18, weight="bold", top=40, left=20, style=ft.TextStyle(shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.BLACK))),
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
            expand=True
        )
    )

ft.app(target=main)