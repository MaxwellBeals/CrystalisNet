import json
import socket
import threading
import os

# Constants for the primary node
PRIMARY_NODE_PORT = 5762
NODES_FILE = 'nodes.json'

# Dictionary to hold nodes
nodes = {}

def load_nodes():
    """Load nodes from the nodes file."""
    if os.path.exists(NODES_FILE):
        with open(NODES_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_nodes(nodes):
    """Save nodes to the nodes file."""
    with open(NODES_FILE, 'w') as file:
        json.dump(nodes, file)

def handle_incoming_connections():
    """Handle incoming connections to the primary node."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', PRIMARY_NODE_PORT))  # Use localhost or specific IP
    server_socket.listen(5)
    print("Primary node listening for incoming connections...")

    while True:
        client_sock, addr = server_socket.accept()
        print(f"Connection from {addr}")

        data = client_sock.recv(1024).decode('utf-8')

        match data:  # Using match to register commands
            case "request_nodes": client_sock.sendall(json.dumps(nodes).encode('utf-8'))  # Send a list of nodes
            case "the_cake": client_sock.sendall('...is a lie!'.encode('utf-8'))  # Example command

            case _:

                # Handle registration of a new node
                try:
                    new_node_id, new_node_ip, new_node_port = json.loads(data)
                    nodes[new_node_id] = (new_node_ip.strip(), int(new_node_port))
                    save_nodes(nodes)
                    print(f"Registered new node: {new_node_id} at {new_node_ip}:{new_node_port}")
                    client_sock.sendall("Node registered successfully.".encode('utf-8'))

                except Exception as e:
                    print(f"Error registering node: {e}")
                    client_sock.sendall("Failed to register node.".encode('utf-8'))

        client_sock.close()

def run_primary_node():
    """Run the primary node."""
    global nodes

    # Load previously saved nodes
    nodes = load_nodes()

    # Start thread to listen for incoming connections
    threading.Thread(target=handle_incoming_connections).start()


# Example usage
if __name__ == "__main__":
    run_primary_node()
