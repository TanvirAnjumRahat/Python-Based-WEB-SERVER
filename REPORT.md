# PyNetLite Project Report

## 1. Introduction
PyNetLite is a from-scratch educational HTTP/1.1 server implemented using Python's `socket` library. It emphasizes clarity over micro-optimizations and demonstrates core networking concepts: connection handling, request parsing, routing, concurrency, caching, and proper response formatting.

## 2. Objectives
- Reinforce understanding of the HTTP/1.1 protocol structure.
- Practice low-level socket programming (no high-level frameworks).
- Demonstrate concurrency using threads.
- Implement static file serving + MIME mapping.
- Provide simple dynamic endpoints (JSON responses) to show extensibility.
- Include lightweight caching to explore trade-offs (latency vs memory).

## 3. Architecture Overview
### Modules
- `server.py`: Entry point, listener loop, thread spawning, graceful shutdown.
- `http.py`: Request parsing (start line, headers, validation) + utilities.
- `response.py`: Response object builder (status line, headers, body encoding).
- `routing.py`: Route registry and dispatch; static vs dynamic separation.
- `cache.py`: Simple LRU cache for small static files.
- `config.py`: Configuration dataclass (host, port, root, max threads, timeouts).
- `utils.py`: Helpers (MIME detection, time formatting, URL decoding, logging).

### Flow
1. Accept TCP connection.
2. Read bytes until CRLF CRLF (headers) or timeout.
3. Parse start line: method, path, version.
4. Parse headers into dict; validate mandatory fields (Host for HTTP/1.1).
5. Determine route type:
   - Static file: map path to `root/path`.
   - Dynamic endpoint: consult `routing.py` dispatcher.
6. Fetch content (cache may supply; else read and possibly insert).
7. Build response (status line, headers incl. `Date`, `Server`, `Connection`).
8. Send response; keep connection open if `keep-alive` and limits not exceeded.
9. Log result; loop for next request or close.

### Concurrency
- One thread per accepted connection (educational simplification).
- Worker handles sequential requests for same socket while keep-alive.

### Caching Strategy
- LRU cache keyed by absolute file path.
- Only caches files below size threshold (default 64KB) and text types.
- Eviction on capacity exceed (default 32 entries).

### Error Handling
- Malformed request -> 400 Bad Request.
- Missing file -> 404 Not Found.
- Exception in handler -> 500 Internal Server Error.

## 4. Key Design Decisions
| Decision | Rationale |
|----------|-----------|
| Threads over `asyncio` | Simpler mental model for course scope. |
| Manual parsing | Reinforces protocol framing concepts. |
| Minimal methods (GET, HEAD) | Focus on fundamentals first. |
| LRU cache | Illustrates temporal locality and eviction strategy. |
| Dynamic routes via dict | Easy extension without framework overhead. |

## 5. Limitations
- No HTTPS (TLS) support.
- Limited method support (no POST file upload parsing).
- Request body handling omitted for simplicity (most endpoints GET only).
- Not production performance; thread-per-connection can exhaust resources under high load.
- Range requests, chunked transfer, compression not implemented.

## 6. Security Considerations
- Prevent directory traversal by normalizing and restricting root path.
- Basic input sanitization (reject paths with `..`).
- No user input execution.

## 7. Testing Strategy
- Unit tests for request parsing (valid & malformed cases).
- Tests for response formatting (status line + headers).
- Manual curl tests for endpoints.

## 8. Future Work
- Add POST and simple body parsing (e.g., form data / JSON).
- Introduce `asyncio` alternative implementation for comparison.
- Add gzip compression and ETag-based caching.
- Implement proper timeout and idle connection limits.
- Basic metrics endpoint `/api/metrics`.

## 9. Conclusion
PyNetLite meets course goals by showing an original, well-structured approach to socket-based HTTP server development while remaining accessible for study and viva demonstration.

## 10. References
- RFC 7230 (HTTP/1.1 Message Syntax and Routing)
- Kurose & Ross Programming Assignments (conceptual inspiration, not copied)
