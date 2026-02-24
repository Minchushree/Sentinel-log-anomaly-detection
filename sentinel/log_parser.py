import re

LOG_PATTERN = re.compile(
    r'(?P<ip>\d+\.\d+\.\d+\.\d+).*?"(?P<method>GET|POST|PUT|DELETE)\s(?P<endpoint>.*?)".*?(?P<status>\d{3})'
)

def parse_log(line):
    match = LOG_PATTERN.search(line)
    if not match:
        return None

    return {
        "ip": match.group("ip"),
        "method": match.group("method"),
        "endpoint": match.group("endpoint"),
        "status": int(match.group("status")),
        "length": len(line)
    }
