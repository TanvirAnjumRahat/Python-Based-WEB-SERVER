import mimetypes
import time
import urllib.parse
from datetime import datetime, timezone
from colorama import Fore, Style

mimetypes.init()

_LOG_COLOR = {
    'INFO': Fore.CYAN,
    'ERROR': Fore.RED,
    'WARN': Fore.YELLOW,
    'DEBUG': Fore.MAGENTA
}

def http_date() -> str:
    return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

def guess_mime(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or 'application/octet-stream'

def url_decode(value: str) -> str:
    return urllib.parse.unquote_plus(value)

def parse_query(query: str) -> dict:
    if not query:
        return {}
    return {k: url_decode(v[0]) if v else '' for k, v in urllib.parse.parse_qs(query, keep_blank_values=True).items()}

def log(level: str, msg: str):
    color = _LOG_COLOR.get(level, '')
    print(f"{color}[{level}] {time.strftime('%H:%M:%S')} {msg}{Style.RESET_ALL}")

def safe_path(root: str, request_path: str) -> str:
    # Prevent directory traversal.
    request_path = request_path.split('?')[0]
    request_path = request_path.lstrip('/')
    norm = request_path.replace('..', '')
    return f"{root}/{norm}" if norm else f"{root}/index.html"
