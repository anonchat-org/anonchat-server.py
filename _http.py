from email import utils
from datetime import datetime, date
from datetime import timezone
from urllib.parse import urlparse, parse_qs

import os, json

try:
    if os.path.exists("./internal.json"):
        with open("./internal.json", "r", encoding="utf-8") as f:
            internal = json.load(f)
except:
    exit("Internal config broken. Re-install server.")

_CURRENT_API = internal["api"]

def htsend(page, client, clients, config):

    # Add example domain, for urlparse and get args and page
    args = parse_qs(urlparse("http://example.com/" + page).query)
    page = urlparse("http://example.com/" + page).path.replace("//", "/")
    
    # _server...
    if page == "/_server/clients":
        send(client, "text/plain", str(len(clients)))
    elif page == "/_server/version":
        send(client, "text/plain", str(_CURRENT_API))
        
    elif page == "/_server/name":
        send(client, "text/plain", config["serverName"])
        
    elif page == "/_server/motd":
        if config["motdEnable"]:
            send(client, "text/plain", config["motd"])
        else:
            send(client, "text/plain", "no")
            
    elif page == "/_server/protocol":
        send(client, "text/plain", config["protocol"])

    # _request...
    elif page == "/_request/send":
        # if user and msg in arguments
        if "user" in args and "msg" in args:
            # If they aren`t out of bounds. As default, 32 for username, and 200 for message contents
            if len(args["user"][0]) <= internal["http"]["message_size"] and len(args["msg"][0]) <= internal["http"]["username_size"]:
                send(client, "text/plain", "ok")
                
                msg = {"user": args["user"][0], "msg": args["msg"][0]}
                text = json.dumps(msg, ensure_ascii=False)

                for c in clients.copy():
                    try:
                        c.sendall(text.encode("utf-8", "replace"))
                    except:
                        clients.remove(c)
                
                return


        htdenied(client) # If message not sent.
        return
    
    # _internal...
    elif page == "/_internal/name":
        send(client, "text/plain", internal["codename"])
    elif page == "/_internal/version":
        send(client, "text/plain", internal["version"])

    # If unknown
    else:
        send(client, "text/html", site)

# https://github.com/pallets/werkzeug
def dt_as_utc(dt):
    if dt is None:
        return dt

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    elif dt.tzinfo != timezone.utc:
        return dt.astimezone(timezone.utc)

    return dt

def http_date(timestamp):
    """Format a datetime object or timestamp into an :rfc:`2822` date
    string.    
    """
    if isinstance(timestamp, date):
        if not isinstance(timestamp, datetime):
            # Assume plain date is midnight UTC.
            timestamp = datetime.combine(timestamp, time(), tzinfo=timezone.utc)
        else:
            # Ensure datetime is timezone-aware.
            timestamp = dt_as_utc(timestamp)

        return utils.format_datetime(timestamp, usegmt=True)

    return utils.formatdate(timestamp, usegmt=True)

def htdenied(sock):
    data = "<h1>Access Denied.</h1>"
    
    text = f"""HTTP/1.0 403 Forbidden
Content-Type: text/html; charset=utf-8
Content-Length: {len(data)}
Server: AnonChat-SRV/3.0
Date: {http_date(datetime.now())}

{data}
""".encode()
    sock.send(text)

    return

def send(sock, ctype, data):
    text = f"""HTTP/1.0 200 OK
Content-Type: {ctype}; charset=utf-8
Content-Length: {len(data)}
Server: AnonChat-SRV/3.0
Date: {http_date(datetime.now())}

{data}
""".encode()
    sock.send(text)

    return 

def get_agent(data):
    for line in data.split("\n"):
        if line.startswith("User-Agent"):
            return line.split(":")[1]

try:
    with open("./index.html", "r", encoding="utf-8") as f:
        site = f.read()
except:
    site = """<h1>AnonChat Server</h1>
No precoded page was loaded :(
"""
