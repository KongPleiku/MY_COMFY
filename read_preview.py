import json
import os
import io
import struct
import requests
from PIL import Image
from src.services.client import ComfyUIClient

# --- Configuration ---
COMFYUI_API_URL = "http://n3.ckey.vn:1609"  # Change this to your ComfyUI server address
WORKFLOW_FILE = "json/GGUF_WORKFLOW_API.json"
OUTPUT_DIR = "previews"


def get_image(filename, subfolder, folder_type, api_url):
    """
    Downloads an image from the ComfyUI server.
    """
    try:
        image_url = f"{api_url}/view?filename={filename}&subfolder={subfolder}&type={folder_type}"
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        return img_response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image {filename}: {e}")
        return None


def main():
    """
    Connects to ComfyUI, runs a workflow, and saves preview and final images.
    """
    # --- 1. Setup ---
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    client = ComfyUIClient(api_url=COMFYUI_API_URL)

    # --- 2. Connect ---
    print(f"Connecting to ComfyUI at {COMFYUI_API_URL}...")
    if not client.connect():
        print("Connection failed.")
        return
    print("Successfully connected.")

    # --- 3. Queue Workflow ---
    try:
        with open(WORKFLOW_FILE, "r") as f:
            workflow = json.load(f)
    except FileNotFoundError:
        print(f"Error: Workflow file not found at {WORKFLOW_FILE}")
        return

    print(f"Queuing workflow from {WORKFLOW_FILE}...")
    response = client.queue_prompt(workflow)
    if not response or "prompt_id" not in response:
        print("Failed to queue prompt.")
        client.close_ws_connection()
        return

    prompt_id = response["prompt_id"]
    print(f"Workflow queued. Prompt ID: {prompt_id}")

    # --- 4. Listen for Messages ---
    print("Listening for messages...")
    preview_counts = {}
    execution_finished = False
    try:
        while not execution_finished:
            msg = client.receive_ws_message()
            if msg is None:
                continue

            if isinstance(msg, bytes):
                # --- Handle Binary Preview Image ---
                if len(msg) > 8:
                    header = msg[:8]
                    event_type, node_id = struct.unpack("!II", header)
                    if event_type == 1:  # Preview image
                        print(f"Received a preview image from node {node_id}.")
                        try:
                            image = Image.open(io.BytesIO(msg[8:]))
                            count = preview_counts.get(node_id, 0)
                            filename = f"preview_node_{node_id}_{count}.png"
                            image.save(os.path.join(OUTPUT_DIR, filename))
                            print(f"Saved preview: {filename}")
                            preview_counts[node_id] = count + 1
                        except Exception as e:
                            print(f"Error processing preview: {e}")
                continue

            # --- Handle Text (JSON) Messages ---
            if "type" in msg:
                print(f"Received message: type='{msg['type']}'")

                if msg["type"] == "executed" and "data" in msg:
                    data = msg["data"]
                    if data.get("prompt_id") == prompt_id:
                        # --- Handle Final Image Output ---
                        if data.get("output", {}).get("images"):
                            print("Received final image data.")
                            images_output = data["output"]["images"]
                            for image_info in images_output:
                                image_data = get_image(
                                    image_info["filename"],
                                    image_info["subfolder"],
                                    image_info["type"],
                                    client.api_url,
                                )
                                if image_data:
                                    try:
                                        image = Image.open(io.BytesIO(image_data))
                                        final_filename = (
                                            f"final_{image_info['filename']}"
                                        )
                                        image.save(
                                            os.path.join(OUTPUT_DIR, final_filename)
                                        )
                                        print(f"Saved final image: {final_filename}")
                                    except Exception as e:
                                        print(f"Error saving final image: {e}")

                        # --- Check for End of Execution ---
                        if data.get("node") is None:
                            print("Execution finished.")
                            execution_finished = True
                            break

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        client.interrupt_generation()
    finally:
        client.close_ws_connection()
        print("WebSocket connection closed.")


if __name__ == "__main__":
    main()
