from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from time import sleep
from zipfile import ZIP_DEFLATED, ZipFile

import httpx


VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


def create_archive(directory: Path) -> Path:
    archive = NamedTemporaryFile(delete=False, suffix=".zip")
    archive_path = Path(archive.name)
    archive.close()
    with ZipFile(archive_path, "w", ZIP_DEFLATED) as zf:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(directory))
    return archive_path


def submit_job(client: httpx.Client, mode: str, task_name: str, archive_path: Path) -> dict:
    endpoint = "/api/skill/jobs/script" if mode == "script" else "/api/skill/jobs/scriptless"
    with archive_path.open("rb") as handle:
        response = client.post(
            endpoint,
            data={"task_name": task_name},
            files={"archive": (archive_path.name, handle, "application/zip")},
        )
    response.raise_for_status()
    return response.json()


def wait_for_completion(client: httpx.Client, task_id: int, poll_interval: float = 2.0) -> dict:
    while True:
        response = client.get(f"/api/skill/jobs/{task_id}")
        response.raise_for_status()
        body = response.json()
        if body.get("status") in {"done", "error"}:
            return body
        if poll_interval > 0:
            sleep(poll_interval)


def download_output(client: httpx.Client, download_url: str, destination: Path) -> Path:
    response = client.get(download_url)
    response.raise_for_status()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)
    return destination

