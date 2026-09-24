"""Deployment entrypoint that adds the optional safe music handlers.

The existing main.py remains unchanged. Start this file with:
    python run.py
"""
from __future__ import annotations

import asyncio

import main as app
from music import MusicController


MUSIC_COMMANDS = {
    "play", "vplay", "pause", "resume", "skip", "end", "queue",
    "volume", "shuffle", "loop", "mutevc", "unmutevc",
}


_original_handle_command = app.handle_command


async def handle_command_without_music(event):
    """Let music.py own music commands; preserve all other main.py behavior."""
    command = event.pattern_match.group(1).lower()
    if command in MUSIC_COMMANDS:
        return
    await _original_handle_command(event)


app.handle_command = handle_command_without_music
music = MusicController(app.client, app.respond)
music.register()


if __name__ == "__main__":
    app.configure_logging()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        pass
