# src/services/config_service.py
import json
import os
from typing import TypedDict, Optional

from utils.logger import get_logger
from services.generation_services import GenerationSetting, FaceDetailerSetting

logger = get_logger(__name__)


class AppConfig(TypedDict):
    generation_setting: GenerationSetting
    face_detailer_setting: Optional[FaceDetailerSetting]
    prompt: str
    connection_url: Optional[str]


class ConfigService:
    def __init__(self, config_filename="config.json"):
        storage_dir = os.getenv("FLET_APP_STORAGE_DATA")
        if storage_dir:
            self.config_path = os.path.join(storage_dir, config_filename)
        else:
            # Fallback for local development
            self.config_path = os.path.join("storage", "data", config_filename)
        self._ensure_config_dir_exists()
        logger.info(f"ConfigService initialized with path: {self.config_path}")

    def _ensure_config_dir_exists(self):
        dir_name = os.path.dirname(self.config_path)
        if not os.path.exists(dir_name):
            logger.info(f"Creating config directory: {dir_name}")
            os.makedirs(dir_name)

    def save_config(self, config: AppConfig):
        logger.info(f"Saving configuration to {self.config_path}")
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}", exc_info=True)

    def load_config(self) -> Optional[AppConfig]:
        logger.info(f"Loading configuration from {self.config_path}")
        if not os.path.exists(self.config_path):
            logger.warning("Config file not found.")
            return None
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
                logger.info("Configuration loaded successfully.")
                return config
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from config file: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Error loading configuration: {e}", exc_info=True)
            return None
