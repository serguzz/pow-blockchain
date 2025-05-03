from src.node import Node
from flask import Flask
from src.node_api import NodeAPI

if __name__ == "__main__":
    app = Flask(__name__)
    node = Node(app=app, node_id="node_003", port=5003, peers=["http://localhost:5000", "http://localhost:5002"])
    api = NodeAPI(app, node)
    node.run()
