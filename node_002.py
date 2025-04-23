from client_node import ClientNode

if __name__ == "__main__":
    client = ClientNode(client_id="node_002", port=5002, peers=["http://localhost:5000"])
    client.run()
