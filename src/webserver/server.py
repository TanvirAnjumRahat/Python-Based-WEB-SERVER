import argparse
import socket
import threading
import os
from pathlib import Path
from typing import Tuple

from .config import ServerConfig
from .http import parse_request, HTTPParseError
from .response import make_response
from .utils import log, guess_mime, safe_path
from .cache import LRUCache
from .routing import router


def handle_connection(conn: socket.socket, addr: Tuple[str, int], config: ServerConfig, cache: LRUCache):
    conn.settimeout(config.timeout)
    requests_handled = 0
    try:
        while requests_handled < config.max_conn_requests:
            # Read headers
            data_chunks = []
            header_complete = False
            while True:
                try:
                    chunk = conn.recv(config.recv_buffer)
                except socket.timeout:
                    log('DEBUG', f"Timeout reading from {addr}")
                    return
                if not chunk:
                    return
                data_chunks.append(chunk)
                joined = b''.join(data_chunks)
                if b'\r\n\r\n' in joined:
                    header_complete = True
                    break
                if len(joined) > config.header_max:
                    raise HTTPParseError('Header too large')
            if not header_complete:
                return
            try:
                request = parse_request(b''.join(data_chunks), config.header_max)
            except HTTPParseError as e:
                resp = make_response(400, str(e).encode(), 'text/plain', keep_alive=False, server_name=config.server_name)
                conn.sendall(resp.to_bytes())
                return
            path = request.path
            # Dynamic route check
            try:
                body, ctype = router.dispatch(path)
                resp = make_response(200, body, ctype, keep_alive=request.keep_alive, server_name=config.server_name)
                conn.sendall(resp.to_bytes())
                log('INFO', f"{addr} {request.method} {path} 200 (dynamic)")
            except KeyError:
                # Static file
                full_path = safe_path(config.root, path)
                p = Path(full_path)
                if not p.exists() or not p.is_file():
                    resp = make_response(404, b'Not Found', 'text/plain', keep_alive=request.keep_alive, server_name=config.server_name)
                    conn.sendall(resp.to_bytes())
                    log('WARN', f"{addr} {request.method} {path} 404")
                else:
                    cached = cache.get(str(p)) if config.cache_enabled else None
                    if cached is None:
                        try:
                            content = p.read_bytes()
                        except OSError:
                            resp = make_response(500, b'Internal Server Error', 'text/plain', keep_alive=False, server_name=config.server_name)
                            conn.sendall(resp.to_bytes())
                            log('ERROR', f"{addr} {request.method} {path} 500 read error")
                            return
                        if config.cache_enabled:
                            cache.put(str(p), content)
                    else:
                        content = cached
                    if request.method == 'HEAD':
                        body_bytes = b''
                    else:
                        body_bytes = content
                    mime = guess_mime(str(p))
                    resp = make_response(200, body_bytes, mime, keep_alive=request.keep_alive, server_name=config.server_name)
                    conn.sendall(resp.to_bytes())
                    source = 'cache' if cached is not None else 'disk'
                    log('INFO', f"{addr} {request.method} {path} 200 ({source})")
            requests_handled += 1
            if not request.keep_alive:
                break
    finally:
        try:
            conn.close()
        except OSError:
            pass


def serve(config: ServerConfig):
    os.makedirs(config.root, exist_ok=True)
    cache = LRUCache(config.cache_max_entries, config.cache_max_file_size)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((config.host, config.port))
        s.listen(config.backlog)
        log('INFO', f"Listening on {config.host}:{config.port} root={config.root}")
        while True:
            try:
                conn, addr = s.accept()
            except OSError as e:
                log('ERROR', f"Accept failed: {e}")
                continue
            t = threading.Thread(target=handle_connection, args=(conn, addr, config, cache), daemon=True)
            t.start()


def parse_args() -> ServerConfig:
    parser = argparse.ArgumentParser(description='PyNetLite HTTP Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--root', default='public')
    parser.add_argument('--no-cache', action='store_true')
    args = parser.parse_args()
    return ServerConfig(host=args.host, port=args.port, root=args.root, cache_enabled=not args.no_cache)

if __name__ == '__main__':
    config = parse_args()
    serve(config)
