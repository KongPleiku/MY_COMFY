# src/components/settings_sheet.py
import flet as ft


class SettingsPanel(ft.Container):
    def __init__(self, page_height, on_close, on_connect_click):
        super().__init__()
        self.on_close_callback = on_close
        self.on_connect_click = on_connect_click

        self.url_field = ft.TextField(
            label="Server URL",
            hint_text="http://127.0.0.1:8188",
            value="http://n3.ckey.vn:1609",
        )

        # --- Tab Content ---
        self.sdxl_tab = ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Row(
                    [ft.Text("High Quality"), ft.Switch(value=True)],
                    alignment="spaceBetween",
                ),
                ft.Row(
                    [ft.Text("Private Mode"), ft.Switch(value=False)],
                    alignment="spaceBetween",
                ),
                ft.Divider(color=ft.colors.GREY_800),
                ft.Text("Steps", color=ft.colors.GREY_400),
                ft.Slider(min=10, max=50, divisions=40, label="{value}", value=20),
            ]
        )

        self.conn_tab = ft.Column(
            controls=[
                ft.Container(height=20),
                self.url_field,
                ft.ElevatedButton(
                    "Test Connection",
                    icon=ft.icons.WIFI,
                    on_click=lambda e: self.on_connect_click(self.url_field.value),
                ),
            ]
        )

        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="SDXL Settings", icon=ft.icons.TUNE, content=self.sdxl_tab),
                ft.Tab(text="Connection", icon=ft.icons.LINK, content=self.conn_tab),
            ],
            expand=True,
        )

        # --- Container Config ---
        self.height = page_height * 0.6
        self.bottom = 0
        self.left = 0
        self.right = 0
        self.bgcolor = ft.colors.GREY_900
        self.border_radius = ft.border_radius.only(top_left=20, top_right=20)
        self.padding = 20
        self.offset = ft.transform.Offset(0, 1)  # Hidden
        self.animate_offset = ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)

        self.content = ft.Column(
            [
                ft.Container(
                    width=40,
                    height=5,
                    bgcolor=ft.colors.GREY_600,
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
                ft.Row(
                    [
                        ft.Text("Settings", size=20, weight="bold"),
                        ft.IconButton(ft.icons.CLOSE, on_click=lambda e: self.close()),
                    ],
                    alignment="spaceBetween",
                ),
                ft.Divider(color=ft.colors.GREY_800),
                self.tabs,
            ]
        )

    def open(self):
        self.tabs.selected_index = 0
        self.offset = ft.transform.Offset(0, 0)
        self.update()

    def close(self):
        self.on_close_callback()
