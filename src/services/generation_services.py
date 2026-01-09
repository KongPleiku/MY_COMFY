# src/services/generation_service.py
import threading
import json
import os
import requests
import base64
from typing import TypedDict, Optional, Literal
from utils.logger import get_logger

logger = get_logger(__name__)


class FaceDetailerSetting(TypedDict):
    steps: int
    cfg: int
    sampler_name: str
    scheduler: str
    denoise: float
    bbox_threshold: float
    bbox_crop_factor: float


class GenerationSetting(TypedDict):
    model: str
    positive_prompt: str
    seed: int
    steps: int
    cfg: int
    sampler_name: str
    scheduler: str
    width: int
    height: int
    Face_detailer_switch: int


class GenerationService:
    def __init__(
        self,
        comfy_client,
        on_progress_update,
        on_status_update,
        on_image_update,
        on_preview_update,
    ):
        self.comfy_client = comfy_client
        self.on_progress_update = on_progress_update  # Callback to update UI bar
        self.on_status_update = on_status_update  # Callback to update UI text
        self.on_image_update = on_image_update  # Callback to update main image
        self.on_preview_update = on_preview_update  # Callback to update preview image
        self._is_generating = False
        self._prompt_id = None
        self._model_loader_node_id = "1"
        self._positive_prompt_node_id = "4"
        self._k_sampler_node_id = "7"
        self._empty_latent_image_node_id = "8"
        self._face_detailer_node_id = "13"
        self._face_detailer_switch_node_id = "21"

    def start_generation(
        self,
        setting: GenerationSetting,
        face_detailer_setting: FaceDetailerSetting | None = None,
    ):
        if self._is_generating:
            logger.warning("Generation already in progress.")
            return

        if not self.comfy_client.is_connected():
            logger.info("Client not connected, attempting to reconnect...")
            self.on_status_update(
                "Connecting...", "Re-establishing link", "BLUE_200", "ORANGE_400"
            )
            if not self.comfy_client.connect():
                logger.error("Failed to reconnect to ComfyUI.")
                self.on_status_update("Error", "Not Connected", "RED_500", "RED_500")
                return

        setting_log = setting.get("positive_prompt")
        logger.info(f"Starting generation for '{setting_log}'")
        self._is_generating = True

        self.on_status_update("Queuing...", "Sending prompt", "BLUE_200", "ORANGE_400")
        self.on_progress_update(0.01)  # Small initial progress

        threading.Thread(
            target=self._real_generation_process,
            args=(
                setting,
                face_detailer_setting,
            ),
            daemon=True,
        ).start()

    def cancel_generation(self):
        if not self._is_generating:
            return
        logger.info("Generation cancelled by user.")
        self._is_generating = False
        self.comfy_client.interrupt_generation()
        if self._prompt_id:
            # Clear the history for the cancelled prompt
            self.comfy_client.get_history(self._prompt_id)
            self._prompt_id = None
        self.on_status_update("Cancelled", "Ready", "WHITE70", "GREEN_400")
        self.on_progress_update(0.0)

    def _real_generation_process(
        self,
        setting: GenerationSetting,
        face_detailer_setting: FaceDetailerSetting | None = None,
    ):
        """The actual generation process that runs in a thread."""
        current_prompt_id = None
        try:
            logger.debug("Loading workflow template from 'assets/GGUF_WORKFLOW_API.json'")
            # 1. Load the workflow template
            with open("assets/GGUF_WORKFLOW_API.json", "r") as f:
                workflow = json.load(f)

            # 2. Modify the workflow with GenerationSetting
            logger.debug(f"Modifying workflow with settings: {setting}")
            workflow[self._model_loader_node_id]["inputs"]["unet_name"] = setting.get(
                "model"
            )

            workflow[self._positive_prompt_node_id]["inputs"]["text"] = setting.get(
                "positive_prompt"
            )

            ksampler = workflow[self._k_sampler_node_id]["inputs"]
            ksampler["seed"] = setting.get("seed")
            ksampler["steps"] = setting.get("steps")
            ksampler["cfg"] = setting.get("cfg")
            ksampler["sampler_name"] = setting.get("sampler_name")
            ksampler["scheduler"] = setting.get("scheduler")
            # Note: "preview_image" should be a string "enable" not a boolean
            ksampler["preview_image"] = "enable"

            latent_image = workflow[self._empty_latent_image_node_id]["inputs"]
            latent_image["width"] = setting.get("width")
            latent_image["height"] = setting.get("height")

            if face_detailer_setting:
                logger.debug(
                    f"Applying face detailer settings: {face_detailer_setting}"
                )
                face_detailer = workflow[self._face_detailer_node_id]["inputs"]
                face_detailer["steps"] = face_detailer_setting.get("steps")
                face_detailer["cfg"] = face_detailer_setting.get("cfg")
                face_detailer["sampler_name"] = face_detailer_setting.get(
                    "sampler_name"
                )
                face_detailer["scheduler"] = face_detailer_setting.get("scheduler")
                face_detailer["denoise"] = face_detailer_setting.get("denoise")
                face_detailer["bbox_threshold"] = face_detailer_setting.get(
                    "bbox_threshold"
                )
                face_detailer["bbox_crop_factor"] = face_detailer_setting.get(
                    "bbox_crop_factor"
                )
                # Use the main seed for the face detailer as well
                face_detailer["seed"] = setting.get("seed")

            workflow[self._face_detailer_switch_node_id]["inputs"][
                "select"
            ] = setting.get(
                "Face_detailer_switch"
            )  # The ImpactInversedSwitch expects 1-indexed values (1 or 2) from the setting.

            # 3. Queue the prompt
            logger.info("Queuing prompt...")
            response = self.comfy_client.queue_prompt(workflow)
            if not response or "prompt_id" not in response:
                raise Exception("Failed to queue prompt or invalid response.")

            self._prompt_id = response["prompt_id"]
            current_prompt_id = self._prompt_id
            logger.info(f"Prompt queued with ID: {self._prompt_id}")
            self.on_status_update(
                "Generating...", f"ID: {self._prompt_id[:8]}", "BLUE_200", "ORANGE_400"
            )

            # 4. Listen to WebSocket for completion and image
            logger.debug("Listening to WebSocket for generation progress...")
            while self._is_generating:
                msg = self.comfy_client.receive_ws_message()
                if msg is None:
                    continue

                if isinstance(msg, bytes):
                    self._handle_preview_image(msg)
                    continue

                if msg["type"] == "progress" and "data" in msg:
                    data = msg["data"]
                    self.on_progress_update(data["value"] / data["max"])

                elif msg["type"] == "executed" and "data" in msg:
                    data = msg["data"]
                    if data.get("output") and "images" in data.get("output"):
                        logger.info("Image data received.")
                        self.on_status_update(
                            "Downloading...", "Receiving image", "CYAN_200", "CYAN_400"
                        )
                        self._handle_image_data(data["output"]["images"])
                        break

                    if (
                        data.get("prompt_id") == self._prompt_id
                        and data.get("node") is None
                    ):
                        logger.info("Execution finished for the prompt.")
                        break

            if not self._is_generating:
                logger.warning("Generation was cancelled before completion.")
                return

            logger.info("Generation finished successfully.")
            self.on_status_update("Finished", "Ready", "WHITE70", "GREEN_400")
            self.on_progress_update(1.0)

        except Exception as e:
            logger.error(f"Generation process failed: {e}", exc_info=True)
            self.on_status_update("Error", "Failed", "RED_500", "RED_500")
        finally:
            if current_prompt_id and self._prompt_id == current_prompt_id:
                self._is_generating = False
                self._prompt_id = None

    def _handle_preview_image(self, image_bytes: bytes):
        """
        Converts the raw image bytes to a base64 string and updates the UI.
        """
        try:
            # The first 8 bytes are header info, we need to strip it
            image_data = image_bytes[8:]
            img_base64 = base64.b64encode(image_data).decode("utf-8")
            self.on_preview_update(img_base64)
            logger.debug("Preview image updated.")
        except Exception as e:
            logger.error(f"Failed to handle preview image: {e}", exc_info=True)

    def _handle_image_data(self, images: list):
        """
        Fetches the last image from the list, converts it to base64,
        and updates the UI via callback.
        """
        if not images:
            logger.warning("No images found in the received data.")
            return

        image_info = images[-1]
        filename = image_info["filename"]
        subfolder = image_info["subfolder"]
        img_type = image_info["type"]
        logger.info(f"Handling final image: {filename}")

        try:
            image_url = f"{self.comfy_client.api_url}/view?filename={filename}&subfolder={subfolder}&type={img_type}"
            logger.debug(f"Fetching image from {image_url}")
            img_response = requests.get(image_url)
            img_response.raise_for_status()

            img_bytes = img_response.content
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

            logger.info(f"Image '{filename}' received and encoded to base64.")
            self.on_image_update(img_base64)

        except Exception as e:
            logger.error(f"Failed to download or encode image: {e}", exc_info=True)
            self.on_status_update("Error", "Image Fetch Failed", "RED_500", "RED_500")
