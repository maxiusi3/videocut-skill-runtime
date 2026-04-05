from pathlib import Path

from videocut_skill.local_validation import detect_mode, validate_directory


def test_detects_script_mode_from_script_and_clip_directories(tmp_path):
    task_dir = tmp_path / "script-task"
    (task_dir / "script").mkdir(parents=True)
    (task_dir / "clip").mkdir()
    (task_dir / "script" / "main.txt").write_text("第一段脚本", encoding="utf-8")
    (task_dir / "clip" / "001.mp4").write_bytes(b"video")

    result = validate_directory(task_dir)

    assert detect_mode(task_dir) == "script"
    assert result.mode == "script"
    assert result.task_name == "script-task"


def test_detects_scriptless_mode_from_top_level_videos(tmp_path):
    task_dir = tmp_path / "scriptless-task"
    task_dir.mkdir()
    (task_dir / "001.mp4").write_bytes(b"video")
    (task_dir / "002.mov").write_bytes(b"video")

    result = validate_directory(task_dir)

    assert detect_mode(task_dir) == "scriptless"
    assert result.mode == "scriptless"
    assert result.clip_files == [task_dir / "001.mp4", task_dir / "002.mov"]
