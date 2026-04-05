from pathlib import Path
import tomllib


def test_package_metadata_matches_public_release_surface():
    root = Path(__file__).resolve().parents[1]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    readme = (root / "README.md").read_text(encoding="utf-8")

    project = pyproject["project"]
    assert project["name"] == "videocut-skill"
    assert project["scripts"]["videocut-skill"] == "videocut_skill.cli:main"
    assert (
        "python3 -m pip install --user --break-system-packages pipx && python3 -m pipx install videocut-skill"
        in readme
    )
