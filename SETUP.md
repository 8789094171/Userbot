# Userbot setup and free run guide

## Required secrets

The bot needs these values:

- `API_ID` and `API_HASH` from https://my.telegram.org
- `SESSION_STRING`, generated locally with:

```bash
python main.py --generate-session
```

Do not commit `.env`, Telegram session files, or a real session string.

## Local run

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python run.py
```

For local runs, export the variables first or load them through your preferred
secret manager. The application creates `runtime/` for logs, state, and
 temporary downloads; that directory is intentionally ignored by Git.

## Docker run

```bash
docker build -t userbot .
docker run --rm -it \\
  -e API_ID="$API_ID" \\
  -e API_HASH="$API_HASH" \\
  -e SESSION_STRING="$SESSION_STRING" \\
  userbot
```

## Free GitHub Actions note

GitHub Actions is suitable for testing or temporary runs, but it is not a
continuous free hosting service: jobs have usage limits and can stop when the
run limit is reached. If you add a workflow manually, store `API_ID`,
`API_HASH`, and `SESSION_STRING` as repository secrets and run `python run.py`.
Never print secrets in workflow logs.

## Current implementation scope

The README lists planned and available commands. `main.py` is the source of
truth for what is executable. Advanced or risky commands may intentionally
return a disabled/guarded response until implemented with permission checks.
