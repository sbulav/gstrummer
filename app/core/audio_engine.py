import threading
from typing import Optional


class AudioEngine:
    def __init__(self):
        self._enabled = True
        
    def play_click(self, accent: bool = False):
        if not self._enabled:
            return
        print("CLICK" + ("!" if accent else ""))
    
    def play_strum(self, direction: str, accent: float = 0.0):
        if not self._enabled:
            return
        accent_str = " (ACCENT)" if accent > 0.5 else ""
        print(f"STRUM {direction}{accent_str}")
    
    def set_enabled(self, enabled: bool):
        self._enabled = enabled
    
    def close(self):
        pass