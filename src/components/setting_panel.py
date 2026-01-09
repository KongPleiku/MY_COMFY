# src/components/setting_panel.py
import flet as ft
import random
from utils.logger import get_logger
from services.generation_services import GenerationSetting, FaceDetailerSetting

logger = get_logger(__name__)


class SettingsPanel(ft.Container):
    def __init__(self, page_height, on_close, on_connect_click, on_change=None):
        super().__init__()
        self.on_close_callback = on_close
        self.on_connect_click = on_connect_click
        self.on_change = on_change
        self._is_setting_from_config = False
        logger.info("SettingsPanel initialized.")

        self.url_field = ft.TextField(
            label="Server URL",
            hint_text="http://127.0.0.1:8188",
            value="http://n3.ckey.vn:1609",
            on_change=self._on_setting_change,
        )
        # --- Controls for GenerationSetting ---
        self.model_field = ft.TextField(
            label="Model", value="WAI_ANI_Q8_0.gguf", on_change=self._on_setting_change
        )
        self.seed_field = ft.TextField(
            label="Seed", value="1", width=150, on_change=self._on_setting_change
        )
        self.width_field = ft.TextField(
            label="Width", value="1024", expand=True, on_change=self._on_setting_change
        )
        self.height_field = ft.TextField(
            label="Height", value="1024", expand=True, on_change=self._on_setting_change
        )

        self.fixed_seed_checkbox = ft.Checkbox(
            label="Fixed", value=True, on_change=self._on_setting_change
        )
        self.randomize_button = ft.IconButton(
            icon=ft.icons.CASINO_OUTLINED,
            tooltip="Randomize Seed",
            on_click=self._randomize_seed,
        )

        self.steps_slider = ft.Slider(
            min=1,
            max=40,
            divisions=39,
            label="Steps: {value}",
            value=20,
            expand=True,  # Added expand=True
            on_change=self._on_setting_change,
        )
        self.cfg_slider = ft.Slider(
            min=1,
            max=10,
            divisions=9,
            label="CFG: {value}",
            value=4,
            expand=True,  # Added expand=True
            on_change=self._on_setting_change,
        )

        self.sampler_dropdown = ft.Dropdown(
            label="Sampler",
            value="euler_ancestral",
            options=[
                ft.dropdown.Option("euler_ancestral"),
                ft.dropdown.Option("euler"),
                ft.dropdown.Option("dpm++_2m_karras"),
            ],
            expand=True,
            on_change=self._on_setting_change,
        )
        self.scheduler_dropdown = ft.Dropdown(
            label="Scheduler",
            value="sgm_uniform",
            options=[
                ft.dropdown.Option("sgm_uniform"),
                ft.dropdown.Option("normal"),
                ft.dropdown.Option("karras"),
                ft.dropdown.Option("simple"),
            ],
            expand=True,
            on_change=self._on_setting_change,
        )

        # --- Controls for FaceDetailer ---
        self.face_detailer_switch = ft.Switch(
            value=False, on_change=self.toggle_face_detailer_settings
        )

        # TextFields for slider values
        self.fd_steps_value = ft.TextField(read_only=True, width=50)
        self.fd_cfg_value = ft.TextField(read_only=True, width=50)
        self.fd_denoise_value = ft.TextField(read_only=True, width=50)
        self.fd_bbox_threshold_value = ft.TextField(read_only=True, width=50)
        self.fd_bbox_crop_factor_value = ft.TextField(read_only=True, width=50)

        self.fd_steps_slider = ft.Slider(
            min=1, max=40, divisions=39, value=20, expand=True
        )  # Added expand=True
        self.fd_cfg_slider = ft.Slider(
            min=1, max=10, divisions=9, value=10, expand=True
        )  # Added expand=True
        self.fd_denoise_slider = ft.Slider(
            min=0.1, max=1.0, divisions=9, value=0.4, expand=True
        )  # Added expand=True
        self.fd_bbox_threshold_slider = ft.Slider(
            min=0.1, max=1.0, divisions=9, value=0.5, expand=True
        )  # Added expand=True
        self.fd_bbox_crop_factor_slider = ft.Slider(
            min=1.0, max=4.0, divisions=30, value=2, expand=True
        )  # Added expand=True

        # Link sliders to their text fields and the generic on_change handler
        self.fd_steps_slider.on_change = lambda e: self._update_slider_textfield(
            e, self.fd_steps_value
        )
        self.fd_cfg_slider.on_change = lambda e: self._update_slider_textfield(
            e, self.fd_cfg_value
        )
        self.fd_denoise_slider.on_change = lambda e: self._update_slider_textfield(
            e, self.fd_denoise_value, "{:.2f}"
        )
        self.fd_bbox_threshold_slider.on_change = (
            lambda e: self._update_slider_textfield(
                e, self.fd_bbox_threshold_value, "{:.2f}"
            )
        )
        self.fd_bbox_crop_factor_slider.on_change = (
            lambda e: self._update_slider_textfield(
                e, self.fd_bbox_crop_factor_value, "{:.2f}"
            )
        )

        self.fd_sampler_dropdown = ft.Dropdown(
            label="Sampler",
            value="euler_ancestral",
            options=[
                ft.dropdown.Option("euler_ancestral"),
                ft.dropdown.Option("euler"),
                ft.dropdown.Option("dpm++_2m_karras"),
            ],
            expand=True,
            on_change=self._on_setting_change,
        )
        self.fd_scheduler_dropdown = ft.Dropdown(
            label="Scheduler",
            value="sgm_uniform",
            options=[
                ft.dropdown.Option("sgm_uniform"),
                ft.dropdown.Option("normal"),
                ft.dropdown.Option("karras"),
                ft.dropdown.Option("simple"),
            ],
            expand=True,
            on_change=self._on_setting_change,
        )

        self.face_detailer_settings_container = ft.Column(
            controls=[
                self._create_slider_row(
                    "Face Detailer Steps", self.fd_steps_slider, self.fd_steps_value
                ),
                self._create_slider_row(
                    "Face Detailer CFG", self.fd_cfg_slider, self.fd_cfg_value
                ),
                ft.Row([self.fd_sampler_dropdown, self.fd_scheduler_dropdown]),
                self._create_slider_row(
                    "Denoise", self.fd_denoise_slider, self.fd_denoise_value
                ),
                self._create_slider_row(
                    "BBox Threshold",
                    self.fd_bbox_threshold_slider,
                    self.fd_bbox_threshold_value,
                ),
                self._create_slider_row(
                    "BBox Crop Factor",
                    self.fd_bbox_crop_factor_slider,
                    self.fd_bbox_crop_factor_value,
                ),
            ],
            visible=False,
            animate_opacity=300,
            spacing=5,
        )

        self.sdxl_tab = ft.Column(
            controls=[
                ft.Container(height=10),
                self.model_field,
                ft.Row(
                    [
                        self.seed_field,
                        self.fixed_seed_checkbox,
                        self.randomize_button,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Row([self.width_field, self.height_field]),
                ft.Text("Steps"),
                self.steps_slider,
                ft.Text("CFG Scale"),
                self.cfg_slider,
                ft.Row([self.sampler_dropdown, self.scheduler_dropdown]),
                ft.Divider(height=10, color="transparent"),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Text("Use Face Detailer"),
                        self.face_detailer_switch,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self.face_detailer_settings_container,
            ],
            scroll=ft.ScrollMode.AUTO,
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
        self.height = page_height * 0.8
        self.bottom = 0
        self.left = 0
        self.right = 0
        self.bgcolor = ft.colors.with_opacity(0.95, ft.colors.GREY_900)
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
                    on_click=lambda e: self.close(),
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
            ],
            expand=True,
        )

    def open(self):
        logger.info("Opening settings panel.")
        self.tabs.selected_index = 0
        self.offset = ft.transform.Offset(0, 0)
        self.update()

    def close(self):
        logger.info("Closing settings panel.")
        self.on_close_callback()

    def _create_slider_row(self, label, slider, value_field):
        return ft.Column(
            [
                ft.Text(label, size=12),
                ft.Row(
                    [
                        slider,
                        value_field,
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=0,
        )

    def toggle_face_detailer_settings(self, e):
        logger.info(f"Toggling face detailer to: {e.control.value}")
        self.face_detailer_settings_container.visible = e.control.value
        self.face_detailer_settings_container.opacity = 1 if e.control.value else 0
        self.update()
        self._on_setting_change(e)

    def _on_setting_change(self, e):
        if not self._is_setting_from_config and self.on_change:
            logger.debug(f"Setting changed by user: {e.control}")
            self.on_change()

    def _update_slider_textfield(self, e, textfield, format_str="{}"):
        textfield.value = format_str.format(e.control.value)
        textfield.update()
        self._on_setting_change(e)

    def _randomize_seed(self, e):
        new_seed = str(random.randint(0, 2**32 - 1))
        logger.info(f"Randomizing seed to: {new_seed}")
        self.seed_field.value = new_seed
        self.update()
        if self.on_change:
            self.on_change()

    def is_seed_fixed(self):
        return self.fixed_seed_checkbox.value

    def _clamp(self, value, min_val, max_val):
        return max(min_val, min(value, max_val))

    def set_settings(
        self,
        gen_settings: GenerationSetting,
        face_detailer_setting: FaceDetailerSetting | None,
    ):
        logger.info("Applying settings from configuration.")
        self._is_setting_from_config = True
        try:
            # General settings
            self.model_field.value = gen_settings.get("model", "WAI_ANI_Q8_0.gguf")
            self.seed_field.value = str(gen_settings.get("seed", "1"))
            self.width_field.value = str(gen_settings.get("width", "1024"))
            self.height_field.value = str(gen_settings.get("height", "1024"))
            self.sampler_dropdown.value = gen_settings.get(
                "sampler_name", "euler_ancestral"
            )
            self.scheduler_dropdown.value = gen_settings.get("scheduler", "sgm_uniform")

            # Clamp slider values
            self.steps_slider.value = self._clamp(
                int(gen_settings.get("steps", 20)),
                self.steps_slider.min,
                self.steps_slider.max,
            )
            self.cfg_slider.value = self._clamp(
                int(gen_settings.get("cfg", 4)),
                self.cfg_slider.min,
                self.cfg_slider.max,
            )

            # Face detailer switch
            use_face_detailer = gen_settings.get("Face_detailer_switch", 1) == 2
            self.face_detailer_switch.value = use_face_detailer
            self.face_detailer_settings_container.visible = use_face_detailer
            self.face_detailer_settings_container.opacity = (
                1 if use_face_detailer else 0
            )

            # Face detailer settings
            if face_detailer_setting:
                self.fd_sampler_dropdown.value = face_detailer_setting.get(
                    "sampler_name", "euler_ancestral"
                )
                self.fd_scheduler_dropdown.value = face_detailer_setting.get(
                    "scheduler", "sgm_uniform"
                )

                # Clamp and set face detailer slider values
                self.fd_steps_slider.value = self._clamp(
                    int(face_detailer_setting.get("steps", 20)),
                    self.fd_steps_slider.min,
                    self.fd_steps_slider.max,
                )
                self.fd_cfg_slider.value = self._clamp(
                    int(face_detailer_setting.get("cfg", 10)),
                    self.fd_cfg_slider.min,
                    self.fd_cfg_slider.max,
                )
                self.fd_denoise_slider.value = self._clamp(
                    float(face_detailer_setting.get("denoise", 0.4)),
                    self.fd_denoise_slider.min,
                    self.fd_denoise_slider.max,
                )
                self.fd_bbox_threshold_slider.value = self._clamp(
                    float(face_detailer_setting.get("bbox_threshold", 0.5)),
                    self.fd_bbox_threshold_slider.min,
                    self.fd_bbox_threshold_slider.max,
                )
                self.fd_bbox_crop_factor_slider.value = self._clamp(
                    float(face_detailer_setting.get("bbox_crop_factor", 2)),
                    self.fd_bbox_crop_factor_slider.min,
                    self.fd_bbox_crop_factor_slider.max,
                )

            # Update text fields with initial values
            self.fd_steps_value.value = str(self.fd_steps_slider.value)
            self.fd_cfg_value.value = str(self.fd_cfg_slider.value)
            self.fd_denoise_value.value = f"{self.fd_denoise_slider.value:.2f}"
            self.fd_bbox_threshold_value.value = (
                f"{self.fd_bbox_threshold_slider.value:.2f}"
            )
            self.fd_bbox_crop_factor_value.value = (
                f"{self.fd_bbox_crop_factor_slider.value:.2f}"
            )

            self.update()
            logger.info("Settings applied successfully.")
        except Exception as e:
            logger.error(f"Error applying settings: {e}", exc_info=True)
        finally:
            self._is_setting_from_config = False

    def get_settings(self) -> tuple[GenerationSetting, FaceDetailerSetting | None]:
        logger.debug("Getting settings from panel.")
        seed = int(self.seed_field.value)
        if not self.fixed_seed_checkbox.value:
            seed = random.randint(0, 2**32 - 1)
            logger.debug(f"Generated new random seed: {seed}")
            self.seed_field.value = str(seed)
            self.update()

        gen_settings: GenerationSetting = {
            "model": self.model_field.value,
            "positive_prompt": "",  # This will be set in the view
            "seed": seed,
            "steps": int(self.steps_slider.value),
            "cfg": int(self.cfg_slider.value),
            "sampler_name": self.sampler_dropdown.value,
            "scheduler": self.scheduler_dropdown.value,
            "width": int(self.width_field.value),
            "height": int(self.height_field.value),
            "Face_detailer_switch": 2 if self.face_detailer_switch.value else 1,
        }

        face_detailer_settings: FaceDetailerSetting | None = None
        if self.face_detailer_switch.value:
            face_detailer_settings = {
                "steps": int(self.fd_steps_slider.value),
                "cfg": int(self.fd_cfg_slider.value),
                "sampler_name": self.fd_sampler_dropdown.value,
                "scheduler": self.fd_scheduler_dropdown.value,
                "denoise": float(self.fd_denoise_slider.value),
                "bbox_threshold": float(self.fd_bbox_threshold_slider.value),
                "bbox_crop_factor": float(self.fd_bbox_crop_factor_slider.value),
            }
        logger.debug(f"Returning settings: {gen_settings}, {face_detailer_settings}")
        return gen_settings, face_detailer_settings
