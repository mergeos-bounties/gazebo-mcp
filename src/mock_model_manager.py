from typing import Dict, Optional
from src.state_manager import StateManager
from src.event_handler import EventHandler

class MockModelManager:
    def __init__(self, state_manager: StateManager, event_handler: EventHandler):
        self.state_manager = state_manager
        self.event_handler = event_handler
        self.mock_models: Dict[str, dict] = {}

    def spawn_model(self, model_name: str, model_data: dict) -> bool:
        """Mock model spawning"""
        if model_name in self.mock_models:
            return False

        self.mock_models[model_name] = model_data
        self.state_manager.update_state(f"model_spawned:{model_name}")
        self.event_handler.handle_event("model_spawn", {"name": model_name, "data": model_data})
        return True

    def delete_model(self, model_name: str) -> bool:
        """Mock model deletion"""
        if model_name not in self.mock_models:
            return False

        del self.mock_models[model_name]
        self.state_manager.update_state(f"model_deleted:{model_name}")
        self.event_handler.handle_event("model_delete", {"name": model_name})
        return True

    def get_model(self, model_name: str) -> Optional[dict]:
        """Get mock model data"""
        return self.mock_models.get(model_name)