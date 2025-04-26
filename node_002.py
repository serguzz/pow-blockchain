from node import Node
from flask import Flask
from node_api import NodeAPI

if __name__ == "__main__":
    app = Flask(__name__)
    node = Node(app=app, node_id="node_002", port=5002, peers=["http://localhost:5000"])
    api = NodeAPI(app, node)
    node.run()
