from dataclasses import dataclass

@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8080
    root: str = "public"
    backlog: int = 64
    max_conn_requests: int = 25  # per keep-alive connection
    recv_buffer: int = 8192
    header_max: int = 16384
    timeout: float = 5.0  # socket read timeout seconds
    cache_enabled: bool = True
    cache_max_entries: int = 32
    cache_max_file_size: int = 64 * 1024  # bytes
    log_enabled: bool = True
    server_name: str = "PyNetLite/0.1"
