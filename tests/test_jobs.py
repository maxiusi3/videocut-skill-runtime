from pathlib import Path
from zipfile import ZipFile

import httpx

from videocut_skill.jobs import create_archive, download_output, wait_for_completion


def test_create_archive_keeps_relative_paths(tmp_path):
    task_dir = tmp_path / "script-task"
    (task_dir / "script").mkdir(parents=True)
    (task_dir / "clip").mkdir()
    (task_dir / "script" / "main.txt").write_text("第一段脚本", encoding="utf-8")
    (task_dir / "clip" / "001.mp4").write_bytes(b"video")

    archive = create_archive(task_dir)

    with ZipFile(archive, "r") as zf:
        assert sorted(zf.namelist()) == ["clip/001.mp4", "script/main.txt"]


def test_wait_for_completion_stops_on_done(monkeypatch):
    responses = iter(
        [
            {
                "task_id": 7,
                "status": "processing",
                "progress": 12,
                "message": "上传完成",
                "output_ready": False,
                "download_url": None,
                "task_url": "/dashboard?task_id=7",
                "error_message": None,
            },
            {
                "task_id": 7,
                "status": "done",
                "progress": 100,
                "message": "已完成",
                "output_ready": True,
                "download_url": "/api/skill/jobs/7/download",
                "task_url": "/dashboard?task_id=7",
                "error_message": None,
            },
        ]
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=next(responses))

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://videocut.example")
    final_status = wait_for_completion(client, task_id=7, poll_interval=0)
    assert final_status["status"] == "done"
    assert final_status["download_url"] == "/api/skill/jobs/7/download"


def test_download_output_writes_bytes(tmp_path):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"video-bytes")

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://videocut.example")
    destination = tmp_path / "final.mp4"

    output = download_output(client, "/api/skill/jobs/7/download", destination)

    assert output == destination
    assert destination.read_bytes() == b"video-bytes"
