# src/services/config_service.py
import json
import os
from typing import TypedDict, Optional

from services.generation_services import GenerationSetting, FaceDetailerSetting


class AppConfig(TypedDict):
    generation_setting: GenerationSetting
    face_detailer_setting: Optional[FaceDetailerSetting]
    prompt: str


class ConfigService:
    def __init__(self, config_path="storage/data/config.json"):
        self.config_path = config_path
        self._ensure_config_dir_exists()

    def _ensure_config_dir_exists(self):
        dir_name = os.path.dirname(self.config_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def save_config(self, config: AppConfig):
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)

    def load_config(self) -> Optional[AppConfig]:
        if not os.path.exists(self.config_path):
            return None
        with open(self.config_path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None
