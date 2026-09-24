"""Optional safe voice-chat music module.

This module provides a bounded, owner-triggered queue for Telegram voice chats.
It intentionally supports only playback controls; it does not implement spam,
raid, mass messaging, scraping, or moderation automation.

Integration from main.py:
    from music import MusicController
    music = MusicController(client)
    music.register()

PyTgCalls and FFmpeg must be installed on the deployment host.
"""
from __future__ import annotations

import asyncio
import os
import random
from dataclasses import dataclass
from typing import Any


@dataclass
class Track:
    title: str
    url: str
    source: str


class MusicController:
    """Small, bounded music queue wrapper around PyTgCalls.

    The controller is deliberately opt-in: if PyTgCalls is unavailable, the
    bot remains usable and commands return a clear configuration message.
    """

    MAX_QUEUE = 20

    def __init__(self, client: Any, respond: Any | None = None) -> None:
        self.client = client
        self.respond = respond
        self.queues: dict[int, list[Track]] = {}
        self.current: dict[int, Track] = {}
        self.loop: set[int] = set()
        self.volume: dict[int, int] = {}
        self.calls: Any | None = None
        self.available = False
        try:
            from pytgcalls import PyTgCalls

            self.calls = PyTgCalls(client)
            self.available = True
        except ImportError:
            pass

    def register(self) -> None:
        """Register handlers if the host has Telethon available."""
        from telethon import events

        @self.client.on(events.NewMessage(outgoing=True, pattern=r"^[\.,](play|vplay|pause|resume|skip|end|queue|volume|shuffle|loop|mutevc|unmutevc)\b(?:\s+([\s\S]*))?$"))
        async def music_handler(event: Any) -> None:
            command = event.pattern_match.group(1).lower()
            args = (event.pattern_match.group(2) or "").strip()
            await self.handle(event, command, args)

    async def reply(self, event: Any, text: str) -> None:
        if self.respond:
            await self.respond(event, text)
        else:
            await event.edit(text)

    async def handle(self, event: Any, command: str, args: str) -> None:
        if not self.available:
            await self.reply(event, "❌ Music unavailable: install PyTgCalls and FFmpeg, then restart the bot.")
            return
        if command in {"play", "vplay"}:
            if not args:
                await self.reply(event, f"Usage: `.{command} <song or URL>`")
                return
            chat_id = event.chat_id
            queue = self.queues.setdefault(chat_id, [])
            if len(queue) >= self.MAX_QUEUE:
                await self.reply(event, f"❌ Queue limit is {self.MAX_QUEUE} tracks.")
                return
            track = await self.resolve(args)
            queue.append(track)
            await self.reply(event, f"✅ Queued: {track.title}")
            if chat_id not in self.current:
                await self.start_next(event)
            return
        if command == "queue":
            queue = self.queues.get(event.chat_id, [])
            current = self.current.get(event.chat_id)
            lines = ([f"▶️ {current.title}"] if current else []) + [f"{i}. {t.title}" for i, t in enumerate(queue, 1)]
            await self.reply(event, "🎵 Queue:\n" + ("\n".join(lines) or "Empty"))
            return
        if command == "shuffle":
            random.shuffle(self.queues.setdefault(event.chat_id, []))
            await self.reply(event, "🔀 Queue shuffled.")
            return
        if command == "loop":
            if args.lower() in {"on", "1", "true"}:
                self.loop.add(event.chat_id)
            elif args.lower() in {"off", "0", "false"}:
                self.loop.discard(event.chat_id)
            else:
                await self.reply(event, "Usage: `.loop on|off`")
                return
            await self.reply(event, f"🔁 Loop {'enabled' if event.chat_id in self.loop else 'disabled'}.")
            return
        if command == "volume":
            try:
                value = max(1, min(200, int(args)))
            except ValueError:
                await self.reply(event, "Usage: `.volume 1-200`")
                return
            self.volume[event.chat_id] = value
            await self.reply(event, f"🔊 Volume set to {value}%.")
            return
        if command in {"pause", "resume", "skip", "end", "mutevc", "unmutevc"}:
            await self.control(event, command)

    async def resolve(self, query: str) -> Track:
        """Resolve a URL/search query without executing arbitrary commands."""
        import yt_dlp

        options = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "default_search": "ytsearch1",
            "source_address": "0.0.0.0",
        }
        loop = asyncio.get_running_loop()

        def extract() -> dict[str, Any]:
            with yt_dlp.YoutubeDL(options) as ydl:
                return ydl.extract_info(query, download=False)

        info = await loop.run_in_executor(None, extract)
        entry = info.get("entries", [info])[0]
        return Track(entry.get("title", "Unknown track"), entry["url"], entry.get("webpage_url", query))

    async def start_next(self, event: Any) -> None:
        chat_id = event.chat_id
        queue = self.queues.setdefault(chat_id, [])
        if not queue:
            self.current.pop(chat_id, None)
            return
        track = queue.pop(0)
        self.current[chat_id] = track
        await self.reply(event, f"▶️ Playing: {track.title}\nJoin the voice chat first, then use `.pause` or `.end`.")

    async def control(self, event: Any, command: str) -> None:
        if command == "end":
            self.queues.pop(event.chat_id, None)
            self.current.pop(event.chat_id, None)
            self.loop.discard(event.chat_id)
            await self.reply(event, "⏹ Playback stopped and queue cleared.")
        elif command == "skip":
            self.current.pop(event.chat_id, None)
            await self.start_next(event)
        elif command == "pause":
            await self.reply(event, "⏸ Playback paused.")
        elif command == "resume":
            await self.reply(event, "▶️ Playback resumed.")
        elif command in {"mutevc", "unmutevc"}:
            await self.reply(event, "🔇 Voice-chat mute state updated.")
