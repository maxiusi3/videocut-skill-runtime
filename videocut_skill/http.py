from __future__ import annotations

import httpx


class RuntimeErrorMessage(Exception):
    pass


def make_client(base_url: str, client_token: str) -> httpx.Client:
    return httpx.Client(
        base_url=base_url.rstrip("/"),
        headers={"Authorization": f"Bearer {client_token}"},
        timeout=60.0,
    )


def raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return

    detail = None
    try:
        body = response.json()
        if isinstance(body, dict):
            detail = body.get("detail") or body.get("message")
    except Exception:
        detail = None

    if not detail:
        detail = response.text.strip() or f"HTTP {response.status_code}"
    raise RuntimeErrorMessage(detail)


def get_json(client: httpx.Client, path: str) -> dict:
    response = client.get(path)
    raise_for_status(response)
    return response.json()

