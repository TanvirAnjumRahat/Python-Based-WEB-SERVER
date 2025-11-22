import json
import time
from typing import Callable, Dict, Tuple
from .utils import parse_query, url_decode

Handler = Callable[[str, Dict[str, str]], Tuple[bytes, str]]  # returns (body, content_type)

class Router:
    def __init__(self):
        self._routes: Dict[str, Handler] = {}
        self.register('/api/time', self._time)
        self.register('/api/echo', self._echo)

    def register(self, path: str, handler: Handler):
        self._routes[path] = handler

    def dispatch(self, path: str) -> Tuple[bytes, str]:
        base, _, query = path.partition('?')
        if base in self._routes:
            params = parse_query(query)
            return self._routes[base](base, params)
        raise KeyError('No dynamic route')

    # Handlers
    def _time(self, _path: str, _params: Dict[str, str]):
        body = json.dumps({'time': time.strftime('%Y-%m-%dT%H:%M:%SZ')}).encode('utf-8')
        return body, 'application/json'

    def _echo(self, _path: str, params: Dict[str, str]):
        msg = params.get('msg', '')
        body = json.dumps({'echo': url_decode(msg)}).encode('utf-8')
        return body, 'application/json'

router = Router()
