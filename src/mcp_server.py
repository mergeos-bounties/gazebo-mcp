# ... existing imports ...
from src.mock.mock_entity_manager import MockEntityManager
from src.live.live_entity_manager import LiveEntityManager

class MCPServer:
    # ... existing code ...

    def setup_routes(self):
        # ... existing routes ...

        # Add new pose-related endpoints
        @self.app.route('/api/v1/entities/<entity_id>/pose', methods=['GET'])
        def get_entity_pose(entity_id):
            try:
                if self.mode == 'mock':
                    return jsonify(MockEntityManager.get_pose(entity_id))
                else:
                    return jsonify(LiveEntityManager.get_pose(entity_id))
            except Exception as e:
                return jsonify({'error': str(e)}), 400

        @self.app.route('/api/v1/entities/<entity_id>/pose', methods=['POST'])
        def set_entity_pose(entity_id):
            try:
                pose_data = request.get_json()
                if not pose_data:
                    return jsonify({'error': 'No pose data provided'}), 400

                if self.mode == 'mock':
                    MockEntityManager.set_pose(entity_id, pose_data)
                else:
                    LiveEntityManager.set_pose(entity_id, pose_data)

                return jsonify({'status': 'success'})
            except Exception as e:
                return jsonify({'error': str(e)}), 400