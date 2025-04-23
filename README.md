# 🧪 Decentralized Blockchain Testnet (Python + Flask)

This is a **testnet-style blockchain simulation** where multiple client nodes mine, validate, and broadcast blocks to each other using **HTTP, Flask, and simple P2P discovery** — all on a single machine or network.

> Built for learning and experimenting with blockchain fundamentals: PoW, P2P networking, consensus, and more.

---

## 🧱 Features

- ⛓️ **Blockchain logic**: blocks, PoW mining, difficulty validation
- 🌐 **Client-server architecture** (or full P2P setup)
- 📡 **Peer discovery** via `/register` and `/peers`
- 🔁 **Block broadcasting** between nodes
- 🧠 **Chain synchronization** (longest chain wins)
- 💻 **Web UI** with real-time log (via SSE), mining button, chain view, and peer list
- 📦 **Data persistence**: blockchain saved in `.csv`
- 🧑‍🤝‍🧑 **Multiple clients** with separate blockchains
- 🔐 **Future-ready**: transaction signatures, balances, conflict resolution

---

## 📁 Structure

blockchain/ 
├── block.py # Block class
├── blockchain.py # Blockchain class
├── client_node.py # ClientNode class (each node runs Flask)
├── genesis_node.py # Genesis node (optional)
├── blockchain/
│ └── blockchain.csv # Persistent chain storage
├── static/
│ └── main.js # JS logic (buttons, SSE)
├── templates/
│ └── index.html # UI layout
├── run_client.sh # Bash script to start new node
├── README.md


---

## 🚀 Running It

### 🧑‍💻 Start a Genesis Node

```bash
python3 server.py

## 🚀 Running It

### 🧑‍💻 Start a Genesis Node

```bash
python3 genesis_node.py
```

The genesis node creates the initial blockchain and exposes `/register`, `/peers`, and `/chain` endpoints.

Accessible at: [http://localhost:5000](http://localhost:5000)

---

### ➕ Start a New Client Node

```bash
python3 client_node.py --port 5001 --peers http://localhost:5001
```

- Replace `5001` with any available port.
- The client registers with its peer(s) and recursively discovers others.
- Accessible at: [http://localhost:5001](http://localhost:5001)

You can run multiple client nodes in different terminals to simulate a peer network.

---

### 🧪 Test the Network

Open your browser and visit a node’s web UI:

- ⛏️ Click **Mine Block** to mine a new block.
- 🔗 View local blockchain at `/view`
- 📡 See connected peers
- 📢 Watch live logs (via SSE) for block mining, syncing, and peer registration
