# PyNetLite Presentation Outline (10+ Minutes)

## Slide 1: Title
- PyNetLite: Educational Python HTTP/1.1 Server
- Your Name, Course, Date

## Slide 2: Motivation
- Learn internals beyond frameworks
- Reinforce networking + protocol parsing
- Original implementation (no copy/paste)

## Slide 3: Objectives
- Raw sockets
- Concurrency
- Routing + static + dynamic
- Caching & performance basics
- Clean architecture & extensibility

## Slide 4: High-Level Architecture
- Diagram: Client -> Listener -> Worker Thread -> Parser -> Router -> Handler -> Response

## Slide 5: Request Lifecycle
1. Accept connection
2. Read + parse
3. Route decision
4. Build response
5. Keep-alive loop

## Slide 6: Module Breakdown
- `server.py`, `http.py`, `response.py`, `routing.py`, `cache.py`, `utils.py`

## Slide 7: HTTP Parsing Highlights
- Start line split
- Header dict
- Validation (Host, method)
- Edge cases handled (malformed lines)

## Slide 8: Concurrency Model
- Thread per connection
- Simplicity vs scalability
- Alternatives: `asyncio` future work

## Slide 9: Static File Handling
- Path normalization
- MIME detection
- 404 / security (no `..` traversal)

## Slide 10: Dynamic Routes
- `/api/time`, `/api/echo`
- Extendable dictionary mapping

## Slide 11: Caching Strategy (LRU)
- In-memory small-file cache
- Eviction policy
- Benefits: latency reduction

## Slide 12: Error Handling
- 400 / 404 / 500
- Graceful logging

## Slide 13: Logging & Observability
- Colored log levels
- Access log line format

## Slide 14: Demo Plan
- Start server
- Curl static file
- Curl JSON endpoints
- Show keep-alive header behavior

## Slide 15: Testing
- Unit tests for parser & response
- Manual curl script

## Slide 16: Limitations
- No TLS
- Limited methods
- Not production scale

## Slide 17: Future Enhancements
- POST, asyncio, gzip, metrics

## Slide 18: Lessons Learned
- Importance of protocol rigor
- Trade-offs (threads vs async)
- Simplicity aids debugging

## Slide 19: Q&A
- Invite questions

## Slide 20: References
- RFC 7230, Course materials

---
Presenter Notes: Aim ~30 seconds per slide; emphasize originality.
