from client_node import ClientNode

if __name__ == "__main__":
    client = ClientNode(client_id="client_002", port=5002)
    client.run()
