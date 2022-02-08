import socket
import sys
import threading
import traceback
import json


def handle(server, client):
    """Incoming messages handler"""
    while True:
        # Receive new data while it's not empty
        # (it happens when the client is disconnected)
        try:
            data = client.recv(2048)
        except:
            data = None

        if not data:
            break

        text = str(data, "utf-8", "replace")

        # If the text is not empty...
        if text.strip():
            # ...then broadcast it to all connected clients

            # But, check if v1 or v2 and package
            try:
                text = json.loads(text)

            except:
                print("[INFO] Got v1 package.")
                text = {"user": "V1-Package", "msg": text}

            text = json.dumps(text, ensure_ascii=False)
            for c in clients.copy():
                try:
                    c.sendall(text.encode("utf-8", "replace"))
                except:
                    clients.remove(c)

    # Remove client on disconnect or error
    try:
        client.close()
        clients.remove(client)
    except:
        pass


if len(sys.argv) < 2:
    exit("Usage: python3 main.py <port>")

# List of connected sockets
clients = set()

# Initialize server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", int(sys.argv[1])))
server.listen()
print(f"[INFO] Running at 0.0.0.0:{sys.argv[1]}")

# Wait for new connection, add it to list, and then run a handler
while True:
    client, addr = server.accept()
    clients.add(client)
    threading.Thread(target=handle, args=(server, client)).start()
