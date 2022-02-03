import socket
import sys
import threading


def handle(server, client, clients):
    """Incoming messages handler"""

    while True:
        # Receive new data while it's not empty
        # (it happens when the client is disconnected)
        data = client.recv(2048)

        if not data:
            break

        text = str(data, "utf-8", "replace")

        # If the text is not empty...
        if text.strip():
            # ...then broadcast it to all connected clients
            for c in clients:
                c.sendall(text.encode("utf-8", "replace"))

    # Remove client on disconnect or error
    clients.remove(client)
    client.close()


if len(sys.argv) < 2:
    exit("Usage: python3 main.py <port>")

# List of connected sockets
clients = set()

# Initialize server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", int(sys.argv[1])))
server.listen()
print(f"Running at 0.0.0.0:{sys.argv[1]}")

# Wait for new connection, add it to list, and then run a handler
while True:
    client, addr = server.accept()
    clients.add(client)
    threading.Thread(target=handle, args=(server, client, clients)).start()
