import requests
import queue
from threading import Thread, Event
from flask import Flask, render_template, jsonify, request, Response
from urllib.parse import urlparse
from blockchain import Blockchain, Block

class ClientNode:
    def __init__(self, client_id, port, peers=None):
        self.client_id = client_id
        self.port = port
        self.node_url = f"http://localhost:{port}"
        self.subscribers = []
        self.stop_event = None  # Event to stop mining thread if needed
        self.peers = set(peers or [])  # Start with known peers
        self.app = Flask(__name__, template_folder='templates')

        self.is_mining = False
        self.mining_thread = None

        # ✅ Initialize blockchain first
        self.blockchain = Blockchain(client_id=client_id)

        self.setup_routes()
        self.register_with_peers()
        self.sync_chain()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return render_template('index.html', client_id=self.client_id)

        # Route to register a new peer
        @self.app.route('/register', methods=['POST'])
        def register():
            data = request.get_json()
            peer_url = data.get("peer")
            if peer_url and (peer_url != self.node_url):
                print(f"{peer_url} is not self node {self.node_url}. Registering...")
                self.peers.add(peer_url)
                print(f"[+] New peer registered: {peer_url}")
            return jsonify({"peers": list(self.peers)})

        # Route to mine a block
        @self.app.route('/mine', methods=['POST'])
        def mine():
            try:
                # new_block = self.mine_block()
                new_block = self.start_mining()
                return jsonify({"message": f"Block {new_block.index} mined and broadcast!"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # Route to receive block from other nodes
        @self.app.route('/receive_block', methods=['POST'])
        def receive_block():
            data = request.get_json()
            miner = data.get("miner")
            block_data = data.get("block")
            try:                
                # Validate the miner URL
                try:
                    parsed = urlparse(miner)
                    if parsed.scheme not in ["http", "https"] or not parsed.netloc:
                        raise ValueError("Invalid URL")
                except Exception as e:
                    print(f"Invalid miner URL: {miner}")
                    return "Invalid miner URL", 400

                # Add miner to peers if it's not self and not already added
                if miner != self.node_url and miner not in self.peers:
                    print(f"[+] Discovered new peer (via block): {miner}")
                    self.peers.add(miner)

                # Get and validate received block
                block = Block.from_dict(block_data)
                latest = self.blockchain.get_latest_block()

                if block.previous_hash != latest.hash:
                    return jsonify({'error': 'Invalid previous hash'}), 400

                if block.difficulty < latest.difficulty:
                    return jsonify({'error': 'Difficulty too low'}), 400

                # stop mining if valid block received
                if hasattr(self, 'stop_event'):
                    self.stop_event.set()
                    print("🛑 Valid incoming block! Any mining will be stopped.")
                '''    
                self.is_mining = False
                if self.mining_thread and self.mining_thread.is_alive():
                    self.mining_thread.join(timeout=1)
                '''

                # Now safely add the received block to the chain
                self.blockchain.chain.append(block)
                print(f"Block {block.index} accepted from {miner}.")                
                self.blockchain.save_chain()
                self.broadcast_to_subscribers(block, miner)  # broadcast to frontend subscribers
                return jsonify({'message': 'Block added'}), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/chain', methods=['GET'])
        def get_chain():
            return [block.__dict__ for block in self.blockchain.chain]
        
        @self.app.route('/peers', methods=['GET'])
        def get_peers():
            return jsonify({"peers": list(self.peers)})
        
        @self.app.route('/sync', methods=['POST'])
        def sync():
            try:
                self.sync_chain()
                return jsonify({"message": "Chain synced with peers!"})
            except Exception as e:
                    return jsonify({"error": str(e)}), 500

        @self.app.route('/stream')
        def stream():
            def event_stream():
                q = queue.Queue()
                self.subscribers.append(q)
                try:
                    while True:
                        data = q.get()
                        yield f"data: {data}\n\n"
                except GeneratorExit:
                    self.subscribers.remove(q)

            return Response(event_stream(), content_type='text/event-stream')

    # Notify subscribers about new block
    def broadcast_to_subscribers(self, block, source=None):
        message = f"✅ Block {block.index} accepted from node: {source}" if source else f"✅ Block {block.index} added"
        for q in self.subscribers:
            try:
                q.put(message)
            except:
                continue

    # Broadcast message to subscribers            
    def broadcast_message(self, message):
        for q in self.subscribers:
            try:
                q.put(message)
            except:
                continue

    def register_with_peers(self):
        known_peers = set(self.peers)
        print(f"Known peers: {known_peers}")
        new_discovered_peers = set()

        for peer_url in list(known_peers):
            print(f"Registering with peer: {peer_url}")
            try:
                res = requests.post(f"{peer_url}/register", json={"peer": self.node_url})
                if res.status_code == 200:
                    received_peers = set(res.json().get("peers", []))
                    discovered_peers = received_peers - known_peers - {self.node_url}
                    new_discovered_peers.update(discovered_peers)
                    self.peers.update(discovered_peers)
                    print(f"[+] Registered with {peer_url} — discovered {len(discovered_peers)} new peer(s)")
            except Exception as e:
                print(f"[!] Failed to register with {peer_url}: {e}")

        # Recursive step: try registering with newly discovered peers
        print(f"Going to register with new discovered peers: {new_discovered_peers}")
        for new_peer in new_discovered_peers:
            if new_peer != self.node_url:
                print(f"Registering with new peer: {new_peer}")
                try:
                    print(f"Sending registration to {new_peer}")
                    res = requests.post(f"{new_peer}/register", json={"peer": self.node_url})
                    print(f"Received response from {new_peer}: {res.status_code}")
                    if res.status_code == 200:
                        received_peers = set(res.json().get("peers", []))
                        self.peers.update(received_peers - {self.node_url})
                        print(f"[+] Recursively registered with {new_peer}")
                except Exception as e:
                    print(f"[!] Failed to register with {new_peer}: {e}")


    # Sync chain with other nodes
    def sync_chain(self):
        longest_chain = self.blockchain.chain
        print(f"Syncing with peers: {self.peers}")
        for peer in self.peers:
            # Skip self node
            if peer == self.node_url:
                continue  # 🔁 Skip self
            print(f"Syncing with {peer}...")
            try:
                res = requests.get(f"{peer}/chain", timeout=3)
                remote_chain_data = res.json()
                remote_chain = [Block.from_dict(b) for b in remote_chain_data]
                
                print (f"Fetched remote chain with {len(remote_chain)} blocks. Validating...")
                
                # Validate the remote chain
                if not remote_chain:
                    print(f"Empty chain from {peer}")
                    continue
                elif not self.blockchain.validate_chain(remote_chain):
                    print(f"Invalid chain from {peer}: malformed")
                    continue

                if len(remote_chain) > len(longest_chain):
                    longest_chain = remote_chain
                elif len(remote_chain) == len(longest_chain):
                    # Choose the chain with the earliest timestamp
                    if remote_chain[-1].timestamp < longest_chain[-1].timestamp:
                        longest_chain = remote_chain
                    # Alternatively, you can compare the hashes of the last blocks
                    # if remote_chain[-1].hash < longest_chain[-1].hash:
            except Exception as e:
                print(f"Could not sync with {peer}: {e}")

        # if len(longest_chain) >= len(self.blockchain.chain):
        if longest_chain != self.blockchain.chain:
            self.blockchain.chain = longest_chain
            self.blockchain.save_chain()
            print(f"[{self.client_id}] Chain updated from peers.")
            self.broadcast_message(f"✅ Chain updated from peers.")
        else:
            print(f"[{self.client_id}] No updates from peers. Current chain is up to date.")
            self.broadcast_message(f"✅ No updates from peers. Current chain is up to date.")

    # Mining in a separate thread
    def start_mining(self):
        def mine_block():
            self.is_mining = True
            self.stop_event = Event()
            self.stop_event.clear()

            self.broadcast_message("⏳ Syncing with peers before mining...")
            self.sync_chain()  # make sure this fetches the longest valid chain

            # Mine and save the new block
            self.broadcast_message(f"⛏️  Mining block...")
            data = f"Mined by {self.client_id}"
            new_block = self.blockchain.mine_block(data, stop_event=self.stop_event)

            # Broadcast the new block to peers
            if new_block is None:
                print("⛔ Mining interrupted on Node level!")
                self.broadcast_message("⛔ Mining interrupted on receiving a valid block!")
                self.is_mining = False
                return None
            # print(f"✅ Mined block {new_block.index} with hash: {new_block.hash} and calculated hash: {new_block.calculate_hash()}. Broadcasting...")
            self.broadcast_block(new_block)
            self.broadcast_to_subscribers(new_block)
            self.is_mining = False  # Stop mining after broadcasting
            # return new_block
        self.mining_thread = Thread(target=mine_block)
        self.mining_thread.start()


    
    def broadcast_block(self, block=None):
        block_data = block.__dict__
        payload = {
            "miner": self.node_url,
            "block": block_data
        }
        for peer in self.peers:
            try:
                r = requests.post(f"{peer}/receive_block", json=payload, timeout=2)
                if r.ok:
                    print(f"Sent block to {peer}")
                else:
                    print(f"{peer} rejected block: {r.text}")
            except Exception as e:
                print(f"Error sending block to {peer}: {e}")

    def run(self):
        # self.register()
        # self.sync_chain()
        self.app.run(port=self.port, debug=False, threaded=True)
