import requests
import websocket  # websocket-client is imported as websocket
import json


class UsageClient:
    def __init__(self, connection):
        self.connection = connection

    def connect(self):
        pass


class ComfyUIClient:
    def __init__(self, api_url="http://127.0.0.1:8188"):
        self.api_url = api_url
        self.client_id = self._generate_client_id()
        self.ws = None  # WebSocket connection

    def _generate_client_id(self):
        import uuid

        return str(uuid.uuid4())

    def connect(self):
        """
        Tests the HTTP connection to the ComfyUI API and establishes a WebSocket connection.
        """
        try:
            # Test HTTP connection
            response = requests.get(f"{self.api_url}/history")  # A common endpoint
            response.raise_for_status()
            print(f"Successfully connected to ComfyUI HTTP API at {self.api_url}")

            # Establish WebSocket connection
            ws_url = f"ws://{self.api_url.split('//')[1]}/ws?clientId={self.client_id}"
            self.ws = websocket.create_connection(ws_url)
            print(f"Successfully connected to ComfyUI WebSocket at {ws_url}")
            return True
        except requests.exceptions.ConnectionError:
            print(
                f"Error: Could not connect to ComfyUI HTTP API at {self.api_url}. Is ComfyUI running?"
            )
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to ComfyUI HTTP API: {e}")
            return False
        except websocket._exceptions.WebSocketConnectionClosedException as e:
            print(f"Error connecting to ComfyUI WebSocket: {e}")
            return False

    def queue_prompt(self, prompt_workflow):
        """
        Queues a prompt to ComfyUI.

        Args:
            prompt_workflow (dict): The JSON object representing the ComfyUI workflow.

        Returns:
            dict: The JSON response from the ComfyUI API, or None if an error occurred.
        """
        if not self.api_url:
            print("ComfyUI API URL is not set.")
            return None

        payload = {"prompt": prompt_workflow, "client_id": self.client_id}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                f"{self.api_url}/prompt", data=json.dumps(payload), headers=headers
            )
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error queuing prompt to ComfyUI: {e}")
            return None

    def get_history(self, prompt_id):
        """
        Retrieves the history for a given prompt_id.
        """
        if not self.api_url:
            print("ComfyUI API URL is not set.")
            return None
        try:
            response = requests.get(f"{self.api_url}/history/{prompt_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting history for prompt {prompt_id}: {e}")
            return None

    def receive_ws_message(self):
        """
        Receives a single message from the WebSocket.
        """
        if self.ws:
            try:
                message = self.ws.recv()
                return json.loads(message)
            except websocket._exceptions.WebSocketConnectionClosedException:
                print("WebSocket connection closed.")
                self.ws = None
            except Exception as e:
                print(f"Error receiving WebSocket message: {e}")
        return None

    def close_ws_connection(self):
        """
        Closes the WebSocket connection.
        """
        if self.ws:
            self.ws.close()
            self.ws = None
            print("WebSocket connection closed.")
