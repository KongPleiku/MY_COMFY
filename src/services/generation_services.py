# src/services/generation_service.py
import threading
import json
import os
import requests
import base64


class GenerationService:
    def __init__(
        self, comfy_client, on_progress_update, on_status_update, on_image_update
    ):
        self.comfy_client = comfy_client
        self.on_progress_update = on_progress_update  # Callback to update UI bar
        self.on_status_update = on_status_update  # Callback to update UI text
        self.on_image_update = on_image_update  # Callback to update main image
        self._is_generating = False
        self._positive_prompt_node_id = (
            "4"  # Node ID for the positive prompt in the workflow
        )

    def start_generation(self, prompt: str):
        if self._is_generating:
            return

        if not self.comfy_client or not self.comfy_client.is_connected():
            print("Service Error: ComfyUI client is not connected.")
            self.on_status_update("Error", "Not Connected", "RED_500", "RED_500")
            return

        print(f"Service: Starting generation for '{prompt}'")
        self._is_generating = True

        self.on_status_update("Queuing...", "Sending prompt", "BLUE_200", "ORANGE_400")
        self.on_progress_update(0.01)  # Small initial progress

        threading.Thread(
            target=self._real_generation_process, args=(prompt,), daemon=True
        ).start()

    def cancel_generation(self):
        if not self._is_generating:
            return
        print("Service: Generation cancelled by user.")
        self._is_generating = False
        self.on_status_update("Cancelled", "Ready", "WHITE70", "GREEN_400")
        self.on_progress_update(0.0)

    def _real_generation_process(self, prompt_text: str):
        """The actual generation process that runs in a thread."""
        try:
            # 1. Load the workflow template
            with open("json/GGUF_WORKFLOW_API.json", "r") as f:
                workflow = json.load(f)

            # 2. Modify the prompt
            workflow[self._positive_prompt_node_id]["inputs"]["text"] = prompt_text

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
