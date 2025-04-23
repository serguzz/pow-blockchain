from flask import Flask, request, Response, jsonify, render_template
import queue
from threading import Lock
from blockchain import Blockchain
from block import Block

subscribers = []
app = Flask(__name__)
chain_lock = Lock()  # Prevent race conditions
peers = set()   # set of peers (nodes in future)

blockchain = Blockchain()
# blockchain.add_block("Genesis Block")  # Only if your chain starts empty

# Notify subscribers about new block
def broadcast_to_subscribers(block):
    data = f"New block #{block.index} added!"
    for q in subscribers:
        q.put(data)

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify([block.__dict__ for block in blockchain.chain]), 200

@app.route('/latest', methods=['GET'])
def get_latest_block():
    latest_block = blockchain.get_latest_block()
    return jsonify(latest_block.__dict__), 200

@app.route('/mine', methods=['POST'])
def receive_mined_block():
    data = request.get_json()

    with chain_lock:
        latest_block = blockchain.get_latest_block()
        expected_index = latest_block.index + 1
        expected_prev_hash = latest_block.hash
        expected_dificulty = latest_block.difficulty

        # difficulty validation (difficulty never declining)
        if data['difficulty'] < expected_dificulty:
            return jsonify({'error': 'Block difficulty too low'}), 400
        # check if block already minted (by a parallel client)
        if data['index'] != expected_index or data['previous_hash'] != expected_prev_hash:
            return jsonify({'error': 'Block already mined by someone else'}), 409

        received_block = Block(
            index=data['index'],
            previous_hash=data['previous_hash'],
            data=data['data'],
            difficulty=data['difficulty'],
            timestamp=data['timestamp'],
            nonce=data['nonce']
        )
        calculated_hash = received_block.calculate_hash()

        if calculated_hash != data['hash'] or not calculated_hash.startswith('0' * received_block.difficulty):
            return jsonify({'error': 'Invalid hash or PoW'}), 400

        blockchain.chain.append(received_block)
        blockchain.save_chain()
        print(f"✅ Block {received_block.index} accepted from client")
        broadcast_to_subscribers(received_block)
        return jsonify(received_block.to_dict()), 201

@app.route('/view')
def view_chain():
    chain_data = [block.to_dict() for block in blockchain.chain]
    return render_template('viewer.html', chain=chain_data)

@app.route('/stream')
def stream():
    def event_stream():
        q = queue.Queue()
        subscribers.append(q)
        try:
            while True:
                data = q.get()
                yield f"data: {data}\n\n"
        except GeneratorExit:
            subscribers.remove(q)

    return Response(event_stream(), content_type='text/event-stream')

# Endpoint to register a new peer
@app.route('/register', methods=['POST'])
def register_peer():
    data = request.get_json()
    peer = data.get('peer')
    if peer and (peer not in peers):
        peers.add(peer)
        print(f"Registered new peer: {peer}")
        return jsonify({'message': 'Peer registered successfully.'}), 200
    return jsonify({'error': 'No peer provided.'}), 400

# Returns json list of registered peers
@app.route('/peers', methods=['GET'])
def get_peers():
    return jsonify(sorted(list(peers))), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True, threaded=True)
