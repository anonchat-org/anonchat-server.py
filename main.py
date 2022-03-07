import socket
import sys
import threading
import traceback
import json
import os

import _http as htclient

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
                # ...if HTTP
                if text.split("\n")[0].split(" ")[-1].startswith("HTTP"):
                    # ...send default page
                    if text.split("\n")[0].startswith("GET"):
                        page = text.split("\n")[0].split(" ")[1]
                        print(f"[INFO] Got HTTP Package with {page} request")
                    else:
                        print(f"[INFO] Got HTTP Package with unknown request")
                        
                    print(f"[INFO] User-Agent is: {htclient.get_agent(text)}")

                    if text.split("\n")[0].startswith("GET"):
                        htclient.htsend(page, client, clients, config)
                    else:
                        htclient.htdenied(client)
                        
                    clients.remove(client)
                    client.close()

                    return
                else:
                    print("[INFO] Got v1 package/Unknown Request. Rejecting connection.")
                    client.send("[SERVER] V1 clients are no longer supported by AnonChat servers from protocol V3 and above. Please update your client to a newer version, or use an outdated server.\nAlso, your client may be using an unknown/broken protocol not understood by the server.\nDisconnected.".encode())
                    clients.remove(client)
                    client.close()

                    return
                
            if not "user" or not "msg" in text:
                print("[INFO] Got Broken Package.")
                
            else:
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

# Read all configs.
if os.path.exists("./server.json"):
    with open("./server.json", "r", encoding="utf-8") as f:
        config = json.load(f)
else:
    print(f"[WARN] Using default server config.")
    config = {
        "serverName": "Server",
        "protocol": "v2",
        "motdEnable": False,
        "motd": '\n// Welcome to the Server!\n',
        "federationToggle": False
    }

    with open("./server.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

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
