from typing import Dict, Any

class StateManager:
    def __init__(self):
        self.state: Dict[str, Any] = {}

    def update_state(self, key: str, value: Any = None) -> None:
        """Update state with mock data"""
        if value is None:
            # For mock operations, we just track the operation
            self.state[key] = True
        else:
            self.state[key] = value

    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return self.state.copy()