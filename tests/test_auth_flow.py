import threading
import urllib.request

from videocut_skill.auth import start_loopback_server, wait_for_callback


def test_loopback_server_captures_bind_code():
    server, callback_url = start_loopback_server()
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    urllib.request.urlopen(f"{callback_url}?request_id=req-1&code=bind-code-1").read()

    request_id, bind_code = wait_for_callback(server, timeout=2)
    assert request_id == "req-1"
    assert bind_code == "bind-code-1"
