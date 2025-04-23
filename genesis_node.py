from flask import jsonify
from client_node import ClientNode

class GenesisNode(ClientNode):
    def setup_routes(self):
        super().setup_routes()

        @self.app.route('/status')
        def status():
            return jsonify({"node": "genesis", "height": len(self.blockchain.chain)})

        # You could add special testing/debug endpoints here

if __name__ == "__main__":
    node = GenesisNode(client_id="genesis_node", port=5000)
    node.run()