import requests
from block import Block

SERVER_URL = "http://127.0.0.1:5000"
DIFFICULTY = 6 # Should match or exceed server-side difficulty
CLIENT_ID = "Jane"

# Step 1: Get the latest block
latest_block_res = requests.get(f'{SERVER_URL}/latest')
latest_block = latest_block_res.json()

# Step 2: Prepare new block data
index = latest_block['index'] + 1
previous_hash = latest_block['hash']
data = f"Mined by client {CLIENT_ID}"
difficulty = DIFFICULTY

# Step 3: Mine block locally
block = Block(index, previous_hash, data, difficulty)
block.mine_block()
print(f"✅ Block mined locally: {block.hash} (nonce: {block.nonce})")

# Step 4: Send mined block to server
res = requests.post(f'{SERVER_URL}/mine', json=block.to_dict())
print("📬 Server response:", res.json())
