from flask import request, jsonify, render_template, Response
import queue
from urllib.parse import urlparse
import os, json

from .block import Block
from .transaction import Transaction
from .wallet import Wallet

class NodeAPI:
    def __init__(self, app, node):
        self.app = app
        self.node = node
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return render_template('index.html', node_id=self.node.node_id)

        @self.app.route('/chain', methods=['GET'])
        def get_chain():
            return [block.__dict__ for block in self.node.blockchain.chain]
        
        @self.app.route('/peers', methods=['GET'])
        def get_peers():
            return jsonify({"peers": list(self.node.peers)})
        
        @self.app.route('/sync', methods=['POST'])
        def sync():
            try:
                self.node.sync_chain()
                return jsonify({"message": "Chain synced with peers!"})
            except Exception as e:
                    return jsonify({"error": str(e)}), 500

        # Route to register a new peer
        @self.app.route('/register', methods=['POST'])
        def register():
            data = request.get_json()
            peer_url = data.get("peer")
            if peer_url and (peer_url != self.node.node_url) and peer_url not in self.node.peers:
                self.node.peers.add(peer_url)
                self.node.broadcast_message(f"[+] Discovered new peer: {peer_url}")
            return jsonify({"peers": list(self.node.peers)})

        @self.app.route('/transactions', methods=['GET'])
        def get_transactions():
            # return json.dump([tx.to_dict() for tx in self.node.pending_transactions], fp=)
            return [tx.to_dict() for tx in self.node.pending_transactions]
            # return [block.__dict__ for block in self.node.blockchain.chain]
            # return jsonify([tx.to_dict() for tx in self.node.pending_transactions])
        

        @self.app.route('/submit_transaction', methods=['POST'])
        def submit_transaction():
            data = request.get_json()

            peer = data.get("peer")
            if peer and peer != self.node.node_url and peer not in self.node.peers:
                self.node.broadcast_message(f"[+] Transaction submitted by unknown peer: {peer}. Registering the peer...")
                self.node.peers.add(peer)

            tx_data = data.get("transaction")
            if not tx_data:
                return jsonify({'error': 'No transaction data provided'}), 400
            
            # Validate the transaction
            tx = Transaction.from_dict(tx_data)
            if not tx.is_valid():
                print(f"⛏️  Invalid transaction: {tx} - Rejecting.")
                return jsonify({'error': 'Invalid transaction'}), 400
            if tx in self.node.pending_transactions:
                print(f"⛏️  Duplicate transaction: {tx} - Rejecting.")
                return jsonify({'message': 'Duplicate transaction'}), 400
            
            self.node.broadcast_message(f"⛏️  New transaction submitted: {tx}")
            self.node.pending_transactions.append(tx)
            self.node.broadcast_transaction(tx)

            # ✅ If not already mining, start mining
            if not self.node.is_mining:
                print(f"⛏️  Starting mining on received transaction.")
                self.node.start_mining()
            return jsonify({'message': 'Transaction accepted'}), 200


        @self.app.route('/submit_transaction_file', methods=['POST'])
        def submit_transaction_file():

            if 'transaction_file' not in request.files:
                return jsonify({"error": "No transaction file provided."}), 400
            transaction_file = request.files['transaction_file']
            if transaction_file.filename == '':
                return jsonify({"error": "No selected file."}), 400
            
            # filename = transaction_file.filename

            # filename = request.args.get('filename')
            # path = os.path.join('transactions', filename)

            '''
            if not os.path.exists(path):
                return jsonify({"error": "Transaction file not found."}), 404

            with open(path, 'r') as f:
                tx_data = json.load(f)

            transaction = Transaction.from_dict(tx_data)
            '''
            transaction = Transaction.from_file_object(transaction_file)
            filename = transaction_file.filename

            if not transaction.is_valid():
                print(f"Invalid transaction in file {filename}.")
                return jsonify({"error": f"Invalid transaction in file {filename}."}), 400

            self.node.broadcast_message(f"⛏️  New transaction submitted from file: {filename}")
            self.node.pending_transactions.append(transaction)
            self.node.broadcast_transaction(transaction)

            # ✅ If not already mining, start mining
            if not self.node.is_mining:
                print(f"⛏️  Starting mining on received transaction.")
                self.node.start_mining()
            # return jsonify({'message': 'Transaction accepted'}), 200

            return jsonify({"message": "Transaction submitted, validated and broadcasted successfully!"}), 200


        # Route to mine a block
        @self.app.route('/mine', methods=['POST'])
        def mine():
            try:
                # Starts asynchronous mining
                self.node.start_mining()
                return jsonify({"message": f"Mining started !!!"})
            except Exception as e:
                print(f"Error starting mining: {e}")
                return jsonify({"error": str(e)}), 500

        # Route to receive block from other nodes
        @self.app.route('/receive_block', methods=['POST'])
        def receive_block():
            data = request.get_json()
            miner = data.get("miner")
            block_data = data.get("block")
            print(f"New block {block_data} received from miner: {miner}")
            try:                
                # Validate the miner URL
                try:
                    parsed = urlparse(miner)
                    if parsed.scheme not in ["http", "https"] or not parsed.netloc:
                        raise ValueError("Invalid URL")
                    print(f"Valid miner URL: {miner}")
                except Exception as e:
                    print(f"Block received from miner with invalid URL: {miner}")
                    return "Invalid miner URL", 400

                # Add miner to peers if it's not self and not already added
                if (miner != self.node.node_url) and (miner not in self.node.peers):
                    self.node.broadcast_message(f"[+] New block submitted by unknown peer: {miner}. Registering the peer...")
                    self.node.peers.add(miner)

                # Get and validate received block
                block = Block.from_dict(block_data)
                latest = self.node.blockchain.get_latest_block()

                if not self.node.blockchain.validate_block(block, latest):
                    print(f"Received block #{block.index} from {miner} does not align with the current chain.")
                    self.node.broadcast_message(f"Could not accept received block #{block.index} from {miner}. Syncing chain instead...")
                    self.node.sync_chain()  # Sync the chain to get the latest chain version
                    latest = self.node.blockchain.get_latest_block()
                    if latest != block:
                        print(f"Received block {block} from {miner} is invalid.")
                        return jsonify({'error': 'Invalid block'}), 400
                    else:
                        print(f"Received block {block} from {miner} is valid after syncing.")
                        # TODO: Maybe need to stop mining if block triggered syncing and
                        # the syncing was successful
                        # self.node.stop_event.set()  # Stop mining if valid block triggered needed syncing
                        # also, check if transactions need to be removed from pending transactions
                        return jsonify({'message': 'Block accepted after syncing'}), 200

                # stop mining if valid block received
                if hasattr(self.node, 'stop_event'):
                    self.node.stop_event.set()
                    print("🛑 Valid incoming block! Any mining will be stopped.")

                # Now safely add the received block to the chain
                self.node.blockchain.chain.append(block)
                # Remove the transactions from pending transactions
                transactions = block.transactions
                if transactions in self.node.pending_transactions:
                    self.node.pending_transactions.remove(transactions)

                self.node.broadcast_message(f"✅ Block {block.index} accepted from {miner}.")
                self.node.blockchain.save_chain()
                # self.node.broadcast_to_subscribers(block, miner)  # broadcast to frontend subscribers
                return jsonify({'message': 'Block added'}), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/stream')
        def stream():
            def event_stream():
                q = queue.Queue()
                self.node.subscribers.append(q)
                try:
                    while True:
                        data = q.get()
                        yield f"data: {data}\n\n"
                except GeneratorExit:
                    self.node.subscribers.remove(q)

            return Response(event_stream(), content_type='text/event-stream')
