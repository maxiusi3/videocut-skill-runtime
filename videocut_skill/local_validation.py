from dataclasses import dataclass
from pathlib import Path
from typing import Literal


VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}
SCRIPT_EXTENSIONS = {".txt", ".md", ".script"}


@dataclass
class ValidationResult:
    mode: Literal["script", "scriptless"]
    task_name: str
    root: Path
    clip_files: list[Path]


def detect_mode(directory: Path) -> Literal["script", "scriptless"]:
    if (directory / "script").is_dir() and ((directory / "clip").is_dir() or (directory / "pip").is_dir()):
        return "script"

    top_level_videos = [
        path for path in sorted(directory.iterdir())
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    ]
    if top_level_videos:
        return "scriptless"
    raise ValueError("目录不符合 Script 或 Scriptless 结构")


def validate_directory(directory: Path) -> ValidationResult:
    if not directory.exists() or not directory.is_dir():
        raise ValueError("目录不存在")

    mode = detect_mode(directory)
    if mode == "script":
        scripts = [
            path for path in sorted((directory / "script").iterdir())
            if path.is_file() and path.suffix.lower() in SCRIPT_EXTENSIONS
        ]
        clips_root = directory / "clip" if (directory / "clip").is_dir() else directory / "pip"
        clips = [
            path for path in sorted(clips_root.iterdir())
            if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
        ]
        if not scripts:
            raise ValueError("Script 模式缺少 script/ 脚本文件")
        if not clips:
            raise ValueError("Script 模式缺少 clip/ 或 pip/ 视频文件")
        return ValidationResult(mode="script", task_name=directory.name, root=directory, clip_files=clips)

    clips = [
        path for path in sorted(directory.iterdir())
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    ]
    return ValidationResult(mode="scriptless", task_name=directory.name, root=directory, clip_files=clips)
