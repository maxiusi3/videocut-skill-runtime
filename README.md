# VideoCut Skill Runtime

VideoCut Skill Runtime is the local CLI used by the public VideoCut paid skill. It keeps hosted rendering, account binding, and point deduction on the VideoCut server, while giving technical users a local command for login, submit, wait, and download.

This package is published on PyPI as `videocut-skill`.

## Requirements

- Python `3.10+`
- `pipx`
- A VideoCut account with available points

## Install

```bash
python3 -m pip install --user --break-system-packages pipx && python3 -m pipx install videocut-skill
```

If `videocut-skill` is not found after installation, run `python3 -m pipx ensurepath`, reopen your shell, and retry.

## First Login

Claude Code:

```bash
videocut-skill login --host claude_code --base-url https://<your-videocut-host>
```

Codex:

```bash
videocut-skill login --host codex --base-url https://<your-videocut-host>
```

The CLI opens a browser window to complete VideoCut account binding and then stores a local client token.

## Common Commands

Submit a task asynchronously:

```bash
videocut-skill generate "/path/to/task-directory" --host claude_code --base-url https://<your-videocut-host>
```

Wait for completion and download automatically:

```bash
videocut-skill generate "/path/to/task-directory" --host claude_code --base-url https://<your-videocut-host> --wait
```

Check job status:

```bash
videocut-skill status 123 --host claude_code --base-url https://<your-videocut-host>
```

Download a finished result:

```bash
videocut-skill download 123 --host claude_code --base-url https://<your-videocut-host> --output ./final.mp4
```

## Supported Task Layouts

Script mode:

```text
task-directory/
  script/main.txt
  clip/
    001.mp4
    002.mp4
```

Scriptless mode:

```text
task-directory/
  001.mp4
  002.mov
```

## Update

```bash
python3 -m pipx upgrade videocut-skill || python3 -m pipx install videocut-skill
```

## Uninstall

```bash
pipx uninstall videocut-skill
```
