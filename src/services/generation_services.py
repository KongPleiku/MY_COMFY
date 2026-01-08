# src/services/generation_service.py
import threading
import json
import os
import requests
import base64
from dataclasses import dataclass, field


@dataclass
class FaceDetailerSetting:
    steps: int = field(default=20)
    cfg: int = field(default=10)


@dataclass
class GenerationSetting:
    model: str = field(default="WAI_ANI_Q8_0.gguf")

    # Prompting
    positive_prompt: str = field(default="")

    # Sampler Setting
    seed: int = field(default=1)
    steps: int = field(default=20)
    cfg: int = field(default=4)
    sampler_name: str = field(default="euler_ancestral")
    scheduler: str = field(default="sgm_uniform")

    # Image size
    width: int = field(default=1024)
    height: int = field(default=1024)

    # Optional
    Face_detailer_switch: int = field(
        default=1
    )  # No face detailer: 1, use face detailer: 2


class GenerationService:
    def __init__(
        self, comfy_client, on_progress_update, on_status_update, on_image_update
    ):
        self.comfy_client = comfy_client
        self.on_progress_update = on_progress_update  # Callback to update UI bar
        self.on_status_update = on_status_update  # Callback to update UI text
        self.on_image_update = on_image_update  # Callback to update main image
        self._is_generating = False
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
            return

        if not self.comfy_client.is_connected():
            print("Client not connected, attempting to reconnect...")
            self.on_status_update(
                "Connecting...", "Re-establishing link", "BLUE_200", "ORANGE_400"
            )
            if not self.comfy_client.connect():
                print("Service Error: Failed to reconnect to ComfyUI.")
                self.on_status_update("Error", "Not Connected", "RED_500", "RED_500")
                return

        print(f"Service: Starting generation for '{setting.positive_prompt}'")
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
        print("Service: Generation cancelled by user.")
        self._is_generating = False
        self.on_status_update("Cancelled", "Ready", "WHITE70", "GREEN_400")
        self.on_progress_update(0.0)

    def _real_generation_process(
        self,
        setting: GenerationSetting,
        face_detailer_setting: FaceDetailerSetting | None = None,
    ):
        """The actual generation process that runs in a thread."""
        try:
            # 1. Load the workflow template
            with open("json/GGUF_WORKFLOW_API.json", "r") as f:
                workflow = json.load(f)

            # 2. Modify the workflow with GenerationSetting
            workflow[self._model_loader_node_id]["inputs"]["unet_name"] = setting.model

            workflow[self._positive_prompt_node_id]["inputs"][
                "text"
            ] = setting.positive_prompt

            ksampler = workflow[self._k_sampler_node_id]["inputs"]
            ksampler["seed"] = setting.seed
            ksampler["steps"] = setting.steps
            ksampler["cfg"] = setting.cfg
            ksampler["sampler_name"] = setting.sampler_name
            ksampler["scheduler"] = setting.scheduler

            latent_image = workflow[self._empty_latent_image_node_id]["inputs"]
            latent_image["width"] = setting.width
            latent_image["height"] = setting.height

            if face_detailer_setting:
                face_detailer = workflow[self._face_detailer_node_id]["inputs"]
                face_detailer["steps"] = face_detailer_setting.steps
                face_detailer["cfg"] = face_detailer_setting.cfg

            workflow[self._face_detailer_switch_node_id]["inputs"][
                "select"
            ] = setting.Face_detailer_switch

            # 3. Queue the prompt
            response = self.comfy_client.queue_prompt(workflow)
            if not response or "prompt_id" not in response:
                raise Exception("Failed to queue prompt or invalid response.")

            prompt_id = response["prompt_id"]
            self.on_status_update(
                "Generating...", f"ID: {prompt_id[:8]}", "BLUE_200", "ORANGE_400"
            )

            # 4. Listen to WebSocket for completion and image
            while self._is_generating:
                msg = self.comfy_client.receive_ws_message()
                if msg is None:
                    continue

                if msg["type"] == "progress" and "data" in msg:
                    data = msg["data"]
                    self.on_progress_update(data["value"] / data["max"])

                elif msg["type"] == "executed" and "data" in msg:
                    data = msg["data"]
                    if "images" in data["output"]:
                        self.on_status_update(
                            "Downloading...", "Receiving image", "CYAN_200", "CYAN_400"
                        )
                        # This will handle fetching the image and updating the UI via callback
                        self._handle_image_data(data["output"]["images"])
                        # Once we have the image, we can break the loop
                        break

                    if data.get("prompt_id") == prompt_id and data.get("node") is None:
                        # End of execution for our prompt
                        break

            if not self._is_generating:
                # If loop was broken by cancellation
                return

            self.on_status_update("Finished", "Ready", "WHITE70", "GREEN_400")
            self.on_progress_update(1.0)  # Ensure it finishes
            # Smoothly fade out progress bar
            threading.Timer(0.5, lambda: self.on_progress_update(0.0)).start()

        except Exception as e:
            print(f"Generation process failed: {e}")
            self.on_status_update("Error", "Failed", "RED_500", "RED_500")
        finally:
            self._is_generating = False

    def _handle_image_data(self, images: list):
        """
        Fetches the last image from the list, converts it to base64,
        and updates the UI via callback.
        """
        if not images:
            return

        # Process the last image in the list, assuming it's the final output
        image_info = images[-1]
        filename = image_info["filename"]
        subfolder = image_info["subfolder"]
        img_type = image_info["type"]

        try:
            image_url = f"{self.comfy_client.api_url}/view?filename={filename}&subfolder={subfolder}&type={img_type}"
            img_response = requests.get(image_url)
            img_response.raise_for_status()

            # Encode the image content to base64
            img_bytes = img_response.content
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

            print(f"Image '{filename}' received and encoded to base64.")
            # Update the main UI with the new image data
            self.on_image_update(img_base64)

        except Exception as e:
            print(f"Failed to download or encode image: {e}")
            self.on_status_update("Error", "Image Fetch Failed", "RED_500", "RED_500")
