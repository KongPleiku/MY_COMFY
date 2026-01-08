import requests
import websocket  # websocket-client is imported as websocket
import json
import uuid


class UsageClient:
    def __init__(self, connection):
        self.connection = connection

    def connect(self):
        pass


class ComfyUIClient:
    def __init__(self, api_url=None):
        self._api_url = api_url
        self._client_id = str(uuid.uuid4())
        self._ws = None  # WebSocket connection
        self._connected = False

    @property
    def api_url(self):
        return self._api_url

    def set_api_url(self, api_url):
        if self._api_url != api_url:
            self._api_url = api_url
            # If URL changes, we should disconnect the old connection
            if self._connected:
                self.close_ws_connection()
                self._connected = False

    def connect(self):
        """
        Tests the HTTP connection to the ComfyUI API and establishes a WebSocket connection.
        Closes any existing WebSocket connection before attempting a new one.
        """
        if not self._api_url:
            print("ComfyUI API URL is not set. Cannot connect.")
            return False

        if self._connected:
            print("Already connected. Closing existing connection before reconnecting.")
            self.close_ws_connection()

        try:
            # Test HTTP connection
            # Using a simple GET request to a known endpoint
            response = requests.get(
                f"{self._api_url}/history", timeout=5
            )  # Add timeout
            response.raise_for_status()
            print(f"Successfully connected to ComfyUI HTTP API at {self._api_url}")

            # Establish WebSocket connection
            # Replace http/https with ws/wss
            ws_protocol = "wss" if self._api_url.startswith("https") else "ws"
            ws_url = f"{ws_protocol}://{self._api_url.split('//')[1]}/ws?clientId={self._client_id}"

            self._ws = websocket.create_connection(ws_url, timeout=5)  # Add timeout
            print(f"Successfully connected to ComfyUI WebSocket at {ws_url}")
            self._connected = True
            return True
        except requests.exceptions.ConnectionError as e:
            print(
                f"Error: Could not connect to ComfyUI HTTP API at {self._api_url}. Is ComfyUI running and accessible? {e}"
            )
            self._connected = False
            return False
        except requests.exceptions.Timeout:
            print(
                f"Error: Connection to ComfyUI HTTP API at {self._api_url} timed out."
            )
            self._connected = False
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to ComfyUI HTTP API: {e}")
            self._connected = False
            return False
        except websocket._exceptions.WebSocketConnectionClosedException as e:
            print(f"Error connecting to ComfyUI WebSocket: {e}")
            self._connected = False
            return False
        except websocket._exceptions.WebSocketTimeoutException:
            print(f"Error: WebSocket connection to {ws_url} timed out.")
            self._connected = False
            return False
        except Exception as e:
            print(f"An unexpected error occurred during connection: {e}")
            self._connected = False
            return False

    def is_connected(self):
        return self._connected and self._ws and self._ws.connected

    def queue_prompt(self, prompt_workflow):
        """
        Queues a prompt to ComfyUI.
        """
        if not self.is_connected():
            print("Not connected to ComfyUI. Cannot queue prompt.")
            return None

        payload = {"prompt": prompt_workflow, "client_id": self._client_id}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                f"{self._api_url}/prompt", data=json.dumps(payload), headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error queuing prompt to ComfyUI: {e}")
            return None

    def get_history(self, prompt_id):
        """
        Retrieves the history for a given prompt_id.
        """
        if not self.is_connected():
            print("Not connected to ComfyUI. Cannot get history.")
            return None
        try:
            response = requests.get(f"{self._api_url}/history/{prompt_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting history for prompt {prompt_id}: {e}")
            return None

    def receive_ws_message(self):
        """
        Receives a single message from the WebSocket.
        Handles both text (JSON) and binary (image preview) messages.
        """
        if self._ws and self._connected:
            try:
                message = self._ws.recv()
                if isinstance(message, str):
                    return json.loads(message)
                elif isinstance(message, bytes):
                    return message  # Return raw bytes for binary messages
            except websocket._exceptions.WebSocketConnectionClosedException:
                print("WebSocket connection closed unexpectedly.")
                self.close_ws_connection()
            except websocket._exceptions.WebSocketTimeoutException:
                return None
            except json.JSONDecodeError:
                print(f"Error decoding JSON from message: {message}")
            except Exception as e:
                print(f"Error receiving WebSocket message: {e}")
        return None

    def interrupt_generation(self):
        """
        Sends an interrupt request to the ComfyUI server.
        """
        if not self.is_connected():
            print("Not connected to ComfyUI. Cannot interrupt.")
            return

        try:
            response = requests.post(f"{self._api_url}/interrupt")
            response.raise_for_status()
            print("Interrupt request sent successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Error sending interrupt request: {e}")

    def close_ws_connection(self):
        """
        Closes the WebSocket connection.
        """
        if self._ws and self._ws.connected:
            self._ws.close()
            print("WebSocket connection closed.")
        self._ws = None
        self._connected = False
