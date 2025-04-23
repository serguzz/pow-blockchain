import requests
from flask import Flask
from blockchain import Blockchain, Block

class ClientNode:
    def __init__(self, client_id, port, server_url="http://localhost:5000"):
        self.client_id = client_id
        self.port = port
        self.peers = set([server_url])  # Start with main server
        self.app = Flask(__name__)
        self.setup_routes()
        self.blockchain = Blockchain(client_id=client_id)

    def setup_routes(self):
        @self.app.route('/receive_block', methods=['POST'])
        def receive_block():
            from flask import request, jsonify
            data = request.get_json()
            try:
                block = Block.from_dict(data)
                latest = self.blockchain.get_latest_block()

                if block.previous_hash != latest.hash:
                    return jsonify({'error': 'Invalid previous hash'}), 400

                if block.difficulty < latest.difficulty:
                    return jsonify({'error': 'Difficulty too low'}), 400

                self.blockchain.chain.append(block)
                self.blockchain.save_chain()
                return jsonify({'message': 'Block added'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/chain', methods=['GET'])
        def get_chain():
            return [block.__dict__ for block in self.blockchain.chain]

    # Register Node with the main server
    def register(self):
        try:
            res = requests.post("http://localhost:5000/register", json={
                "client_id": self.client_id,
                "url": f"http://localhost:{self.port}"
            })
            peers = res.json().get("peers", [])
            self.peers.update(peers)
        except Exception as e:
            print(f"Registration failed: {e}")


    # Sync with other nodes
    def sync_chain(self):
        longest_chain = self.blockchain.chain
        for peer in self.peers:
            print(f"Syncing with {peer}...")
            try:
                res = requests.get(f"{peer}/chain", timeout=3)
                remote_chain_data = res.json()
                remote_chain = [Block.from_dict(b) for b in remote_chain_data]

                if len(remote_chain) > len(longest_chain):
                    longest_chain = remote_chain
                elif len(remote_chain) == len(longest_chain):
                    if remote_chain[-1].hash < longest_chain[-1].hash:
                        longest_chain = remote_chain
            except Exception as e:
                print(f"Could not sync with {peer}: {e}")

        if len(longest_chain) >= len(self.blockchain.chain):
            self.blockchain.chain = longest_chain
            self.blockchain.save_chain()
            print(f"[{self.client_id}] Chain updated from peers.")


    def mine_block(self):
        latest = self.blockchain.get_latest_block()
        data = f"Mined by client {self.client_id}"
        new_block = Block(
            index=len(self.blockchain.chain),
            previous_hash=latest.hash,
            transactions=[data],
            difficulty=self.blockchain.difficulty
        )
        new_block.mine_block()

        self.blockchain.chain.append(new_block)
        self.blockchain.save_chain()
        print(f"Block {new_block.index} mined. Broadcasting...")

        self.broadcast_block(new_block)

    
    def broadcast_block(self, block):
        block_data = block.__dict__
        for peer in self.peers:
            try:
                r = requests.post(f"{peer}/receive_block", json=block_data, timeout=2)
                if r.ok:
                    print(f"Sent block to {peer}")
                else:
                    print(f"{peer} rejected block: {r.text}")
            except Exception as e:
                print(f"Error sending block to {peer}: {e}")

    def run(self):
        self.register()
        self.sync_chain()
        self.app.run(port=self.port)
