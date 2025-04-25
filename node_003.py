from node import Node

if __name__ == "__main__":
    client = Node(node_id="node_003", port=5003, peers=[
        "http://localhost:5000",
        "http://localhost:5002"
        ])
    client.run()
