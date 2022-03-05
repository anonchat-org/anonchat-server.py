from email import utils
from datetime import datetime, date
from datetime import timezone

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

def send(sock):
    text = f"""HTTP/1.0 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: {len(site)}
Server: AnonChat-SRV/2.0
Date: {http_date(datetime.now())}

{site}
""".encode()
    sock.send(text)

    return 

def get_uagent(data):
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
