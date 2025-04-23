from client_node import ClientNode

if __name__ == "__main__":
    client = ClientNode(client_id="node_003", port=5003, peers=[
        "http://localhost:5000",
        "http://localhost:5002"
        ])
    client.run()
