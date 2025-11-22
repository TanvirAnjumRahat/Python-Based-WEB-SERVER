# PyNetLite Web Server

A lightweight educational Python HTTP/1.1 web server built from raw sockets for learning core networking concepts (request parsing, status codes, persistent connections, concurrency, caching, routing, and static file delivery). Designed to be original (not copy/paste) while aligning to course objectives.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [API](#api)
- [Design Overview](#design-overview)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation
```powershell
# Clone (replace with your repo URL once pushed)
git clone https://github.com/yourusername/pynetlite.git
cd pynetlite

# (Optional) create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage
```powershell
# Run server (default: 127.0.0.1:8080)
python -m src.webserver.server --port 8080 --root public
```
Visit: http://localhost:8080/

Example API call:
```powershell
curl http://localhost:8080/api/time
```

## Features
- Raw socket HTTP/1.1 parsing (methods: GET, HEAD)
- Persistent connections with `Connection: keep-alive`
- Concurrent handling via threads
- Static file serving with MIME detection
- Simple route dispatcher (`/`, `/api/time`, `/api/echo?msg=...`)
- Graceful error responses (404, 400, 500)
- Basic in-memory file caching (LRU)
- Configurable via CLI flags & config object
- Access logging with colored output

## API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves index.html if present else welcome text |
| `/api/time` | GET | Returns JSON server time |
| `/api/echo?msg=hello` | GET | Returns JSON echo of message |

Example response:
```json
{"time": "2025-11-21T12:34:56Z"}
```

## Design Overview
See `REPORT.md` for deep architecture notes (modules, flow diagram, concurrency model, limitations, future work).

## Contributing
Contributions are welcome! Please open issues / PRs. For larger changes, discuss design first.

## License
MIT License (add LICENSE file before publishing).

## Contact
Maintainer: Your Name (https://github.com/yourusername)
