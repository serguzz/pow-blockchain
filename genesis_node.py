from flask import Flask, jsonify
from node import Node
from node_api import NodeAPI

class GenesisNode(Node):
    def __init__(self, app, node_id, port, peers=None):
        super().__init__(app=app, node_id=node_id, port=port, peers=peers)
        # Define additional routes for the genesis node

        @self.app.route('/status')
        def status():
            return jsonify({"node": "genesis", "height": len(self.blockchain.chain)})

        # You could add special testing/debug endpoints here

if __name__ == "__main__":
    app = Flask(__name__)
    node = GenesisNode(app=app, node_id="genesis_node", port=5000)
    api = NodeAPI(app, node)
    node.run()