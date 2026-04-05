from __future__ import annotations

import argparse
from pathlib import Path
import webbrowser

import httpx

from videocut_skill.auth import start_loopback_server, wait_for_callback
from videocut_skill.http import make_client, raise_for_status
from videocut_skill.jobs import create_archive, download_output, submit_job, wait_for_completion
from videocut_skill.local_validation import validate_directory
from videocut_skill.state import StateStore, StoredBinding


DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def _load_binding(base_url: str, host: str) -> StoredBinding | None:
    binding = StateStore().load()
    if not binding:
        return None
    if binding.base_url.rstrip("/") != base_url.rstrip("/") or binding.host != host:
        return None
    return binding


def _login(args: argparse.Namespace) -> int:
    store = StateStore()
    server, callback_url = start_loopback_server()
    start_response = httpx.post(
        f"{args.base_url.rstrip('/')}/api/skill/auth/start",
        json={
            "host": args.host,
            "client_label": args.client_label,
            "redirect_uri": callback_url,
            "site_base_url": args.base_url,
        },
        timeout=30.0,
    )
    raise_for_status(start_response)
    payload = start_response.json()
    webbrowser.open(payload["authorize_url"])
    request_id, bind_code = wait_for_callback(server)

    exchange_response = httpx.post(
        f"{args.base_url.rstrip('/')}/api/skill/auth/exchange",
        json={"request_id": request_id, "bind_code": bind_code},
        timeout=30.0,
    )
    raise_for_status(exchange_response)
    token_payload = exchange_response.json()

    store.save(
        StoredBinding(
            base_url=args.base_url,
            host=args.host,
            client_id=token_payload["client_id"],
            client_token=token_payload["client_token"],
            expires_at=token_payload["expires_at"],
        )
    )
    print("VideoCut skill 登录完成。")
    return 0


def _ensure_binding(args: argparse.Namespace) -> StoredBinding:
    binding = _load_binding(args.base_url, args.host)
    if binding:
        return binding
    login_args = argparse.Namespace(
        base_url=args.base_url,
        host=args.host,
        client_label=args.client_label,
    )
    _login(login_args)
    refreshed = _load_binding(args.base_url, args.host)
    if not refreshed:
        raise SystemExit("浏览器授权未完成")
    return refreshed


def _generate(args: argparse.Namespace) -> int:
    binding = _ensure_binding(args)
    validation = validate_directory(args.directory)
    client = make_client(binding.base_url, binding.client_token)
    archive = create_archive(args.directory)
    try:
        job = submit_job(client, validation.mode, validation.task_name, archive)
    finally:
        archive.unlink(missing_ok=True)

    StateStore().record_task(job["task_id"], job["task_url"], str(args.directory))
    print(f"任务已提交: #{job['task_id']} {job['task_url']}")

    if not args.wait:
        return 0

    final_status = wait_for_completion(client, job["task_id"])
    if final_status.get("status") != "done":
        raise SystemExit(final_status.get("error_message") or "任务失败")

    output_path = args.output or (args.directory / f"{validation.task_name}_final.mp4")
    download_output(client, final_status["download_url"], output_path)
    print(f"成片已下载到: {output_path}")
    return 0


def _status(args: argparse.Namespace) -> int:
    binding = _ensure_binding(args)
    client = make_client(binding.base_url, binding.client_token)
    response = client.get(f"/api/skill/jobs/{args.task_id}")
    raise_for_status(response)
    body = response.json()
    print(f"任务 #{body['task_id']}: {body['status']} ({body['progress']}%)")
    return 0


def _download(args: argparse.Namespace) -> int:
    binding = _ensure_binding(args)
    client = make_client(binding.base_url, binding.client_token)
    response = client.get(f"/api/skill/jobs/{args.task_id}")
    raise_for_status(response)
    body = response.json()
    if not body.get("download_url"):
        raise SystemExit("任务尚未生成完成")

    output = args.output or Path.cwd() / f"videocut-task-{args.task_id}.mp4"
    download_output(client, body["download_url"], output)
    print(f"成片已下载到: {output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="videocut-skill")
    sub = parser.add_subparsers(dest="command", required=True)

    login = sub.add_parser("login")
    login.add_argument("--base-url", default=DEFAULT_BASE_URL)
    login.add_argument("--host", choices=["claude_code", "codex"], default="claude_code")
    login.add_argument("--client-label", default="VideoCut Skill Client")
    login.set_defaults(func=_login)

    generate = sub.add_parser("generate")
    generate.add_argument("directory", type=Path)
    generate.add_argument("--wait", action="store_true")
    generate.add_argument("--output", type=Path)
    generate.add_argument("--base-url", default=DEFAULT_BASE_URL)
    generate.add_argument("--host", choices=["claude_code", "codex"], default="claude_code")
    generate.add_argument("--client-label", default="VideoCut Skill Client")
    generate.set_defaults(func=_generate)

    status = sub.add_parser("status")
    status.add_argument("task_id", type=int)
    status.add_argument("--base-url", default=DEFAULT_BASE_URL)
    status.add_argument("--host", choices=["claude_code", "codex"], default="claude_code")
    status.add_argument("--client-label", default="VideoCut Skill Client")
    status.set_defaults(func=_status)

    download = sub.add_parser("download")
    download.add_argument("task_id", type=int)
    download.add_argument("--output", type=Path)
    download.add_argument("--base-url", default=DEFAULT_BASE_URL)
    download.add_argument("--host", choices=["claude_code", "codex"], default="claude_code")
    download.add_argument("--client-label", default="VideoCut Skill Client")
    download.set_defaults(func=_download)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
