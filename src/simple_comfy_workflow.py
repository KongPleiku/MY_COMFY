import time
import json
import requests
import os
from services.client import ComfyUIClient


def main():
    # Initialize the ComfyUI client
    # Assuming ComfyUI is running locally on the default port 8188
    comfy_client = ComfyUIClient(api_url="http://n3.ckey.vn:1609")  # Reverted API URL

    # Connect to ComfyUI
    print("Attempting to connect to ComfyUI...")
    if not comfy_client.connect():
        print("Failed to connect to ComfyUI. Please ensure ComfyUI is running.")
        return

    print("Connected to ComfyUI.")

    # Load a sample ComfyUI workflow (replace with your actual workflow JSON)
    try:
        with open("json/GGUF_WORKFLOW_API.json", "r") as f:
            prompt_workflow = json.load(f)
    except FileNotFoundError:
        print("Error: json/GGUF_WORKFLOW_API.json not found.")
        print("Please provide a valid ComfyUI workflow JSON file.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from json/GGUF_WORKFLOW_API.json.")
        return

    print("Sample workflow loaded. Queuing prompt...")
    # Queue the prompt
    response = comfy_client.queue_prompt(prompt_workflow)

    if response:
        print("Prompt queued successfully!")
        print("Response:", json.dumps(response, indent=2))

        prompt_id = response.get("prompt_id")
        if prompt_id:
            print(f"Waiting for prompt {prompt_id} to complete...")

            # Listen to WebSocket for real-time updates
            while True:
                ws_message = comfy_client.receive_ws_message()
                if ws_message:
                    # print(f"WS Message: {json.dumps(ws_message, indent=2)}") # Uncomment for debugging
                    if ws_message["type"] == "progress":
                        data = ws_message["data"]
                        print(
                            f"Progress: {data['value']}/{data['max']} ({data['value']/data['max']*100:.1f}%)"
                        )

                    elif ws_message["type"] == "executed":
                        data = ws_message["data"]
                        # Check if this node is the one that produced the output we want
                        if "images" in data["output"]:
                            print("Image data found in WebSocket message.")
                            for image_data in data["output"]["images"]:
                                try:
                                    # For "Preview Image" nodes, the image data is sent directly
                                    image_url = f"{comfy_client.api_url}/view?filename={image_data['filename']}&subfolder={image_data['subfolder']}&type={image_data['type']}"
                                    print(f"Fetching image from: {image_url}")

                                    img_response = requests.get(image_url)
                                    img_response.raise_for_status()

                                    # Ensure the storage/temp directory exists
                                    output_dir = "storage/temp"
                                    os.makedirs(output_dir, exist_ok=True)
                                    output_path = os.path.join(
                                        output_dir, image_data["filename"]
                                    )

                                    with open(output_path, "wb") as img_file:
                                        img_file.write(img_response.content)

                                    print(f"Image saved to: {output_path}")

                                except requests.exceptions.RequestException as e:
                                    print(f"Error fetching image: {e}")
                                except Exception as e:
                                    print(f"An error occurred: {e}")

                        # Check for end of execution
                        if (
                            data.get("prompt_id") == prompt_id
                            and data.get("node") is None
                        ):
                            print(f"Execution for prompt {prompt_id} finished.")
                            break
                else:
                    # If no message, the connection might be closed
                    print("No WebSocket message received. Connection might be closed.")
                    break
        else:
            print("No prompt_id in the response.")
    else:
        print("Failed to queue prompt.")

    # Close the WebSocket connection
    comfy_client.close_ws_connection()
    print("Disconnected from ComfyUI.")


if __name__ == "__main__":
    main()
