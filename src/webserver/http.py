from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class HTTPRequest:
    method: str
    path: str
    version: str
    headers: Dict[str, str]

    @property
    def keep_alive(self) -> bool:
        connection = self.headers.get('connection', '').lower()
        if self.version == 'HTTP/1.1':
            return connection != 'close'
        return connection == 'keep-alive'

SUPPORTED_METHODS = {'GET', 'HEAD'}

class HTTPParseError(Exception):
    pass

def parse_request(raw: bytes, header_max: int) -> HTTPRequest:
    if len(raw) > header_max:
        raise HTTPParseError('Header section too large')
    try:
        text = raw.decode('iso-8859-1')  # permissive
    except UnicodeDecodeError:
        raise HTTPParseError('Invalid encoding')
    parts = text.split('\r\n\r\n', 1)
    header_block = parts[0]
    lines = header_block.split('\r\n')
    if not lines:
        raise HTTPParseError('Empty request')
    start = lines[0]
    try:
        method, path, version = start.split(' ', 2)
    except ValueError:
        raise HTTPParseError('Malformed start line')
    if method.upper() not in SUPPORTED_METHODS:
        raise HTTPParseError('Unsupported method')
    headers = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        if ':' not in line:
            raise HTTPParseError('Malformed header line')
        name, value = line.split(':', 1)
        headers[name.strip().lower()] = value.strip()
    # Basic HTTP/1.1 compliance: Host header required.
    if version == 'HTTP/1.1' and 'host' not in headers:
        raise HTTPParseError('Missing Host header')
    return HTTPRequest(method=method.upper(), path=path, version=version, headers=headers)
