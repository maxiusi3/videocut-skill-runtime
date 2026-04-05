from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import List, Optional


STATE_PATH = Path.home() / ".videocut-skill" / "state.json"


@dataclass
class RecentTask:
    task_id: int
    task_url: str
    local_directory: str
    created_at: str


@dataclass
class StoredBinding:
    base_url: str
    host: str
    client_id: str
    client_token: str
    expires_at: str
    nickname: str | None = None
    recent_tasks: List[RecentTask] = field(default_factory=list)


class StateStore:
    def __init__(self, path: Path = STATE_PATH):
        self.path = path

    def load(self) -> Optional[StoredBinding]:
        if not self.path.exists():
            return None
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        raw["recent_tasks"] = [RecentTask(**task) for task in raw.get("recent_tasks", [])]
        return StoredBinding(**raw)

    def save(self, binding: StoredBinding) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(binding), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def record_task(self, task_id: int, task_url: str, local_directory: str) -> None:
        binding = self.load()
        if not binding:
            return
        binding.recent_tasks = [
            RecentTask(
                task_id=task_id,
                task_url=task_url,
                local_directory=local_directory,
                created_at=datetime.utcnow().isoformat(),
            )
        ] + binding.recent_tasks[:9]
        self.save(binding)
