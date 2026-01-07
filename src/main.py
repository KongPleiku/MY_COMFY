import flet as ft

def main(page: ft.Page):
    # Android/Mobile specific setup
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK 
    
    image_src = "https://picsum.photos/1080/1920"

    # --- helper: Animation Function ---
    def toggle_settings(e):
        # If currently hidden (offset y=1), move to visible (y=0)
        if settings_panel.offset.y == 1:
            settings_panel.offset = ft.transform.Offset(0, 0)
        else:
            # Move back down (y=1)
            settings_panel.offset = ft.transform.Offset(0, 1)
        page.update()

    # --- Layer 4: The Settings Panel (Hidden by default) ---
    # We create this first so we can reference it in the buttons
    settings_panel = ft.Container(
        # Dimensions
        height=page.height * 0.75, # Take up 3/4 of screen height
        bottom=0, left=0, right=0, # Anchor to bottom
        
        # Styling
        bgcolor=ft.colors.GREY_900,
        border_radius=ft.border_radius.only(top_left=20, top_right=20),
        padding=20,
        
        # Animation Properties
        offset=ft.transform.Offset(0, 1), # Start pushed down (OFF SCREEN)
        animate_offset=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT), # Smooth slide
        
        # Content of the Settings Page
        content=ft.Column(
            controls=[
                # A little handle bar at the top
                ft.Container(
                    width=40, height=5, 
                    bgcolor=ft.colors.GREY_600, 
                    border_radius=10, 
                    alignment=ft.alignment.center
                ),
                ft.Row(
                    controls=[
                        ft.Text("Settings", size=24, weight="bold"),
                        ft.IconButton(ft.icons.CLOSE, on_click=toggle_settings)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                ft.Switch(label="Dark Mode", value=True),
                ft.Switch(label="Notifications", value=False),
                ft.Slider(min=0, max=100, label="Volume"),
                ft.ElevatedButton("Log Out", color=ft.colors.RED_400)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    page.add(
        ft.Stack(
            controls=[
                # --- Layer 1: The Interactive Background Image ---
                ft.InteractiveViewer(
                    min_scale=1.0,
                    max_scale=5.0,
                    boundary_margin=ft.margin.all(0),
                    content=ft.Image(
                        src=image_src,
                        fit=ft.ImageFit.COVER,
                        height=page.height,
                        width=page.width,
                    )
                ),

                # --- Layer 2: Status Text ---
                ft.Text(
                    value="Status: Connected",
                    size=18,
                    color=ft.colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                    top=40, left=20,
                    style=ft.TextStyle(shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.BLACK))
                ),

                # --- Layer 3: The Control Bar ---
                ft.Container(
                    bottom=20, left=20, right=20,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            # Left: WIFI
                            ft.FloatingActionButton(
                                icon=ft.icons.WIFI,
                                bgcolor=ft.colors.BLACK54,
                                on_click=lambda _: print("Connection clicked"),
                            ),

                            # Center: Group [GEN] [X]
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.FloatingActionButton(
                                        text="GEN",
                                        icon=ft.icons.AUTO_AWESOME,
                                        width=120,
                                        shape=ft.RoundedRectangleBorder(radius=30),
                                        on_click=lambda _: print("Generation clicked"),
                                    ),
                                    ft.FloatingActionButton(
                                        mini=True, 
                                        icon=ft.icons.CLOSE,
                                        bgcolor=ft.colors.RED_900,
                                        shape=ft.CircleBorder(),
                                        on_click=lambda _: print("Cancel clicked"),
                                    ),
                                ]
                            ),

                            # Right: SETTINGS (Triggers the panel)
                            ft.FloatingActionButton(
                                icon=ft.icons.SETTINGS,
                                bgcolor=ft.colors.BLACK54,
                                on_click=toggle_settings, # <--- Calls our function
                            ),
                        ]
                    )
                ),
                
                # --- Layer 4: The Sliding Settings Panel ---
                # Must be added LAST so it sits ON TOP of everything else
                settings_panel
            ],
            expand=True
        )
    )

ft.app(target=main)