from http.server import BaseHTTPRequestHandler, HTTPServer
import time


class _LoopbackServer(HTTPServer):
    request_id: str | None = None
    bind_code: str | None = None


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        from urllib.parse import parse_qs, urlparse

        params = parse_qs(urlparse(self.path).query)
        self.server.request_id = params.get("request_id", [None])[0]
        self.server.bind_code = params.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("VideoCut skill 授权完成，请回到终端。".encode("utf-8"))

    def log_message(self, format, *args):  # noqa: A003
        return


def start_loopback_server():
    server = _LoopbackServer(("127.0.0.1", 0), _CallbackHandler)
    host, port = server.server_address
    return server, f"http://{host}:{port}/callback"


def wait_for_callback(server, timeout: int = 180):
    deadline = time.time() + timeout
    while time.time() < deadline:
        server.timeout = 0.2
        server.handle_request()
        if server.request_id and server.bind_code:
            return server.request_id, server.bind_code
    raise TimeoutError("等待浏览器授权超时")
