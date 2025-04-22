from flask import Flask, request, jsonify
from blockchain import Blockchain
from block import Block

app = Flask(__name__)
blockchain = Blockchain()
blockchain.add_block("Genesis Block")  # Only if your chain starts empty

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

    latest_block = blockchain.get_latest_block()
    expected_index = latest_block.index + 1
    expected_prev_hash = latest_block.hash
    expected_dificulty = latest_block.difficulty

    # Basic validation
    if data['index'] != expected_index or data['previous_hash'] != expected_prev_hash:
        return jsonify({'error': 'Invalid block index or previous hash'}), 400

    if data['difficulty'] < expected_dificulty:
        return jsonify({'error': 'Block difficulty too low'}), 400

    # Recreate and verify hash
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
    print(f"✅ Block {received_block.index} accepted from client")
    return jsonify(received_block.to_dict()), 201

if __name__ == '__main__':
    app.run(port=5000, debug=True, threaded=True)
