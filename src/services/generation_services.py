# src/services/generation_service.py
import threading
import time

class GenerationService:
    def __init__(self, on_progress_update, on_status_update):
        self.on_progress_update = on_progress_update # Callback to update UI bar
        self.on_status_update = on_status_update     # Callback to update UI text
        self._is_generating = False

    def start_generation(self, prompt: str):
        if self._is_generating:
            return

        print(f"Service: Starting generation for '{prompt}'")
        self._is_generating = True
        
        # Notify UI: Generating State
        self.on_status_update("Generating...", "Processing", "BLUE_200", "ORANGE_400")
        self.on_progress_update(0.1) # Immediate jump

        # Simulate work (normally you'd call an API here)
        # We use a separate thread so we don't freeze the UI
        threading.Thread(target=self._mock_generation_process, daemon=True).start()

    def cancel_generation(self):
        print("Service: Generation cancelled")
        self._is_generating = False
        # Notify UI: Idle State
        self.on_status_update("Idle", "Ready", "WHITE70", "GREEN_400")
        self.on_progress_update(0.0)

    def _mock_generation_process(self):
        """Simulates a backend process taking time"""
        steps = [0.3, 0.5, 0.8, 1.0]
        for step in steps:
            if not self._is_generating: return # Stop if cancelled
            time.sleep(1.0) # Fake processing time
            self.on_progress_update(step)
        
        if self._is_generating:
            # Done
            self._is_generating = False
            self.on_status_update("Idle", "Finished", "WHITE70", "GREEN_400")