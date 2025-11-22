from dataclasses import dataclass, field
from typing import Dict, Union
from .utils import http_date

@dataclass
class HTTPResponse:
    status_code: int
    reason: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Union[bytes, None] = None

    def to_bytes(self) -> bytes:
        status_line = f"HTTP/1.1 {self.status_code} {self.reason}\r\n"
        hdrs = ''.join(f"{k}: {v}\r\n" for k, v in self.headers.items())
        end = '\r\n'
        return (status_line + hdrs + end).encode('iso-8859-1') + (self.body or b'')

REASONS = {
    200: 'OK',
    400: 'Bad Request',
    404: 'Not Found',
    500: 'Internal Server Error'
}

def make_response(status_code: int, body: bytes = b'', content_type: str = 'text/plain; charset=utf-8', keep_alive: bool = True, server_name: str = 'PyNetLite/0.1') -> HTTPResponse:
    reason = REASONS.get(status_code, 'OK')
    headers = {
        'Date': http_date(),
        'Server': server_name,
        'Content-Length': str(len(body)),
        'Content-Type': content_type,
        'Connection': 'keep-alive' if keep_alive and status_code < 500 else 'close'
    }
    return HTTPResponse(status_code=status_code, reason=reason, headers=headers, body=body if body else b'' )
