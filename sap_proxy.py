#!/usr/bin/env python3
"""
SAP OData CORS Proxy Server  —  Python edition
================================================
No dependencies. Uses only Python built-in libraries.
Works on Windows, Mac, Linux with Python 3.6+.

USAGE:
  python3 sap_proxy.py           # listens on port 3100
  python3 sap_proxy.py 3101      # custom port

In the SAP Security Analyzer app:
  Connection → Mode: Proxy → Proxy URL: http://localhost:3100
"""

import json, base64, urllib.request, urllib.error, urllib.parse, ssl, sys, os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 3100))

CORS_HEADERS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age":       "86400",
}

# Ignore self-signed certs on SAP dev/QA systems
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode    = ssl.CERT_NONE


class ProxyHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"  [{self.log_date_time_string()}]  {fmt % args}")

    # ── Send response with CORS headers ──────────────────────────────
    def send_json(self, code, body_dict):
        body_bytes = json.dumps(body_dict).encode()
        self.send_response(code)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.send_header("Content-Type",   "application/json")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    # ── Preflight ────────────────────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    # ── Health check ─────────────────────────────────────────────────
    def do_GET(self):
        if self.path in ("/", "/health"):
            self.send_json(200, {"status": "ok", "port": PORT, "service": "SAP OData CORS Proxy"})
        else:
            self.send_json(404, {"error": "Not found. POST to /proxy"})

    # ── Main proxy endpoint ──────────────────────────────────────────
    def do_POST(self):
        if self.path != "/proxy":
            self.send_json(404, {"error": "Not found"})
            return

        # Read request body
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length))
        except Exception:
            self.send_json(400, {"error": "Invalid JSON body"})
            return

        target   = body.get("url",      "")
        username = body.get("username", "")
        password = body.get("password", "")

        if not target:
            self.send_json(400, {"error": "Missing field: url"})
            return

        print(f"  -> {target[:100]}")

        # Build Basic Auth header
        token = base64.b64encode(f"{username}:{password}".encode()).decode()

        req = urllib.request.Request(
            target,
            headers={
                "Authorization": f"Basic {token}",
                "Accept":        "application/json",
                "Content-Type":  "application/json",
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=15) as resp:
                raw  = resp.read().decode("utf-8", errors="replace")
                code = resp.status
                try:
                    data = json.loads(raw)
                except Exception:
                    data = {"raw": raw}
                print(f"  <- HTTP {code}")
                self.send_json(200, {"ok": True, "status": code, "data": data})

        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                err_data = json.loads(raw)
            except Exception:
                err_data = {"raw": raw[:500]}
            print(f"  <- SAP HTTP {e.code}")
            self.send_json(200, {"ok": False, "status": e.code, "data": err_data})

        except urllib.error.URLError as e:
            print(f"  !! URLError: {e.reason}")
            self.send_json(502, {"ok": False, "error": str(e.reason)})

        except Exception as e:
            print(f"  !! Error: {e}")
            self.send_json(502, {"ok": False, "error": str(e)})


# ── Entry point ──────────────────────────────────────────────────────
if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), ProxyHandler)

    print()
    print("  ┌────────────────────────────────────────────────┐")
    print("  │   SAP OData CORS Proxy  —  Python edition      │")
    print("  ├────────────────────────────────────────────────┤")
    print(f"  │   Listening on  http://0.0.0.0:{PORT:<5}           │")
    print(f"  │   Proxy URL     http://localhost:{PORT:<5}          │")
    print("  │   Health check  GET  /health                   │")
    print("  │   Proxy call    POST /proxy                    │")
    print("  └────────────────────────────────────────────────┘")
    print()
    print("  In the SAP Security Analyzer:")
    print(f"  → Connection → Mode: Proxy → Proxy URL: http://localhost:{PORT}")
    print()
    print("  Press Ctrl+C to stop.")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Proxy stopped.")
        server.server_close()
