from client_node import ClientNode

if __name__ == "__main__":
    client = ClientNode(client_id="client_003", port=5003)
    client.run()
