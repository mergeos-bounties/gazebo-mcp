from typing import Dict, Any, Callable

class EventHandler:
    def __init__(self):
        self.event_handlers: Dict[str, Callable] = {}

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler"""
        self.event_handlers[event_type] = handler

    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle mock events"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type](event_data)