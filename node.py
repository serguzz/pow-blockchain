import requests
import queue
from threading import Thread, Event
from flask import Flask, render_template, jsonify, request, Response
from urllib.parse import urlparse
from blockchain import Blockchain, Block

class Node:
    def __init__(self, app, node_id, port, peers=None):
        self.node_id = node_id
        self.port = port
        self.node_url = f"http://localhost:{port}"
        self.subscribers = []
        self.stop_event = None  # Event to stop mining thread if needed
        self.peers = set(peers or [])  # Start with known peers
        # self.app = Flask(__name__, template_folder='templates')
        self.app = app

        self.pending_transactions = []  # List to hold pending transactions
        self.is_mining = False
        self.mining_thread = None

        # ✅ Initialize blockchain first
        self.blockchain = Blockchain(node_id=node_id)

        # self.setup_routes()
        self.register_with_peers()
        self.sync_chain()


    # Notify subscribers about new block
    def broadcast_to_subscribers(self, block, source=None):
        message = f"✅ Block {block.index} accepted from node: {source}" if source else f"✅ Block {block.index} mined, saved and broadcasted."
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
            print(f"[{self.node_id}] Chain updated from peers.")
            self.broadcast_message(f"✅ Chain updated from peers.")
        else:
            print(f"[{self.node_id}] No updates from peers. Current chain is up to date.")
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
            transactions_data = self.pending_transactions[0] if self.pending_transactions else "empty"
            data = f"'{transactions_data}' mined by {self.node_id}"
            self.broadcast_message(f"⛏️  Mining block with data: {data}, stop_event: {self.stop_event.isSet()}")
            new_block = self.blockchain.mine_block(data, stop_event=self.stop_event)

            if new_block is None:
                print("⛔ Mining interrupted on Node level!")
                self.broadcast_message("⛔ Mining interrupted on receiving a valid block!")
                self.is_mining = False
                # If mining was interrupted, check if more transactions in the pool
                # and start mining again
                if self.pending_transactions:
                    self.broadcast_message("🔁 More transactions in the pool. Starting mining again...")
                    self.start_mining() # Recursive call to mine next block
                return None
            
            # Remove the mined transaction from the pool
            if transactions_data in self.pending_transactions:
                self.pending_transactions.remove(transactions_data)
            # Broadcast the new block to peers
            self.broadcast_block(new_block)
            self.broadcast_to_subscribers(new_block)
            self.is_mining = False  # Stop mining after broadcasting

            # ✅ Check if more transactions are still in the pool
            if self.pending_transactions:
                self.broadcast_message("🔁 Continuing mining pending transactions...")
                self.start_mining()  # Recursive call to mine next block

            # return new_block
        self.mining_thread = Thread(target=mine_block)
        self.mining_thread.start()

    def broadcast_transaction(self, transaction):
        payload = {
            "transaction": transaction,
            "peer": self.node_url
        }
        for peer in self.peers:
            try:
                r = requests.post(f"{peer}/submit_transaction", json=payload, timeout=2)
                if r.ok:
                    print(f"Sent transaction to {peer}")
                else:
                    print(f"{peer} rejected transaction: {r.text}")
            except Exception as e:
                print(f"Error sending transaction to {peer}: {e}")


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
        self.app.run(port=self.port, debug=False, threaded=True)
        # self.register()
        # self.sync_chain()
