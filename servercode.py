import json
import os
import random
import hashlib
import socket
import threading

# Constants for file paths
UNMINTED_COINS_FILE = 'unminted_coins.json'
MINTED_COINS_FILE = 'minted_coins.json'
NODES_FILE = 'nodes.json'

# Dictionary to hold nodes
nodes = {}

def initialize_files():
    """Initialize the necessary JSON files."""
    if not os.path.exists(UNMINTED_COINS_FILE):
        with open(UNMINTED_COINS_FILE, 'w') as file:
            json.dump({}, file)  # Create empty JSON file

    if not os.path.exists(MINTED_COINS_FILE):
        with open(MINTED_COINS_FILE, 'w') as file:
            json.dump({}, file)  # Create empty JSON file

    if not os.path.exists(NODES_FILE):
        with open(NODES_FILE, 'w') as file:
            json.dump({}, file)  # Create empty JSON file

def load_coins(file_path):
    """Load coins from a specified file."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}

def save_coins(file_path, coins):
    """Save coins to a specified file."""
    with open(file_path, 'w') as file:
        json.dump(coins, file)

def load_unminted_coins():
    """Load unminted coins from file."""
    return load_coins(UNMINTED_COINS_FILE)

def save_unminted_coins(unminted_coins):
    """Save unminted coins to file."""
    save_coins(UNMINTED_COINS_FILE, unminted_coins)

def load_minted_coins():
    """Load minted coins from file."""
    return load_coins(MINTED_COINS_FILE)

def save_minted_coins(minted_coins):
    """Save minted coins to file."""
    save_coins(MINTED_COINS_FILE, minted_coins)

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

def connect_to_node(ip, port):
    """Connect to a node."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        return sock
    except Exception as e:
        print(f"Error connecting to node {ip}:{port} - {e}")
        return None

def register_with_primary_node(primary_ip, primary_port):
    """Register with the primary node to get the list of other nodes."""
    try:
        sock = connect_to_node(primary_ip, primary_port)
        if sock:
            sock.sendall("request_nodes".encode('utf-8'))
            data = sock.recv(1024).decode('utf-8')
            sock.close()
            new_nodes = json.loads(data)
            return new_nodes
        else:
            print(f"Failed to reach primary node {primary_ip}")
    except Exception as e:
        print(f"Error fetching nodes from primary node {primary_ip}: {e}")
    return {}

def fetch_coins_from_random_node(request_type):
    """Fetch coins from a random node."""
    if not nodes:
        print("No nodes available to fetch keys from.")
        return {}

    random_node_id = random.choice(list(nodes.keys()))
    node_ip, node_port = nodes[random_node_id]
    
    try:
        sock = connect_to_node(node_ip, node_port)
        if sock:
            sock.sendall(request_type.encode('utf-8'))
            data = sock.recv(1024).decode('utf-8')
            sock.close()
            return json.loads(data)
        else:
            print(f"Failed to reach random node {random_node_id}")
    except Exception as e:
        print(f"Error fetching keys from node {random_node_id}: {e}")
    return {}

def fetch_unminted_coins_from_random_node():
    """Fetch unminted coins from a random node."""
    return fetch_coins_from_random_node("request_unminted_coins")

def fetch_minted_coins_from_random_node():
    """Fetch minted coins from a random node."""
    return fetch_coins_from_random_node("request_minted_coins")

def fetch_checksum_from_random_node():
    """Fetch checksum from a random node."""
    return fetch_coins_from_random_node("request_checksum")

def validate_unminted_coins(unminted_coins, checksum):
    """Validate unminted coins against a checksum."""
    combined_keys = ''.join(unminted_coins.keys())
    calculated_checksum = hashlib.sha256(combined_keys.encode()).hexdigest()
    return calculated_checksum == checksum

def validate_minted_coins(minted_coins, checksum):
    """Validate minted coins against a checksum."""
    combined_keys = ''.join(minted_coins.keys())
    calculated_checksum = hashlib.sha256(combined_keys.encode()).hexdigest()
    return calculated_checksum == checksum

def handle_incoming_connections(port):
    """Handle incoming connections to the node."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))  # Use localhost or specific IP
    server_socket.listen(5)
    print("Listening for incoming connections...")

    while True:
        client_sock, addr = server_socket.accept()
        print(f"Connection from {addr}")

        data = client_sock.recv(1024).decode('utf-8')
        if data == "request_unminted_coins":
            client_sock.sendall(json.dumps(unminted_coins).encode('utf-8'))
        elif data == "request_minted_coins":
            client_sock.sendall(json.dumps(minted_coins).encode('utf-8'))
        elif data == "request_checksum":
            combined_keys = ''.join(unminted_coins.keys()) + ''.join(minted_coins.keys())
            checksum = hashlib.sha256(combined_keys.encode()).hexdigest()
            client_sock.sendall(checksum.encode('utf-8'))
        elif data == "request_nodes":
            client_sock.sendall(json.dumps(nodes).encode('utf-8'))
        else:
            # Handle other incoming data as needed
            print(f"Received unknown request: {data}")

        client_sock.close()

def run_node(node_ip, node_port, primary_node_ip=None, primary_node_port=None):
    """Run the node with the specified IP and port."""
    global unminted_coins, minted_coins, nodes

    initialize_files()

    # Load previously saved coins and nodes
    unminted_coins = load_unminted_coins()
    minted_coins = load_minted_coins()
    nodes = load_nodes()

    # Register with primary node if provided
    if primary_node_ip and primary_node_port:
        new_nodes = register_with_primary_node(primary_node_ip, primary_node_port)
        nodes.update(new_nodes)
        save_nodes(nodes)

    # Fetch keys from a random node
    new_unminted_coins = fetch_unminted_coins_from_random_node()
    new_minted_coins = fetch_minted_coins_from_random_node()

    unminted_coins.update(new_unminted_coins)
    minted_coins.update(new_minted_coins)

    # Fetch checksums from random nodes
    checksum_unminted = fetch_checksum_from_random_node()
    checksum_minted = fetch_checksum_from_random_node()

    if checksum_unminted and validate_unminted_coins(unminted_coins, checksum_unminted):
        print("Checksum for unminted coins is valid. Updating stored coins.")
        save_unminted_coins(unminted_coins)
    else:
        print("Checksum for unminted coins is invalid. Not updating coins.")

    if checksum_minted and validate_minted_coins(minted_coins, checksum_minted):
        print("Checksum for minted coins is valid. Updating stored coins.")
        save_minted_coins(minted_coins)
    else:
        print("Checksum for minted coins is invalid. Not updating coins.")

    # Start thread to listen for incoming connections
    threading.Thread(target=handle_incoming_connections, args=(node_port,)).start()

# Example usage
if __name__ == "__main__":
    NODE_IP = '127.0.0.1'  # Replace with your public IP if needed
    NODE_PORT = 5762
    PRIMARY_NODE_IP = '127.0.0.1'  # Primary node to contact for the rest of the nodes
    PRIMARY_NODE_PORT = 5763  # Port of the primary node
    run_node(NODE_IP, NODE_PORT, PRIMARY_NODE_IP, PRIMARY_NODE_PORT)
