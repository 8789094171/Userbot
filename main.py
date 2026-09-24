"""Owner-only Telegram userbot foundation.

Local development:
    API_ID=... API_HASH=... python main.py

GitHub Actions:
    API_ID, API_HASH, and SESSION_STRING must be repository secrets.

Generate a Telethon StringSession locally, then save the printed value as
SESSION_STRING:
    API_ID=... API_HASH=... python main.py --generate-session

This userbot intentionally keeps shell execution, arbitrary Python evaluation,
secret output, spying, and unrestricted forwarding disabled.
"""

from __future__ import annotations

import asyncio
import ast
import json
import logging
import operator
import os
import shutil
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.photos import (
    DeletePhotosRequest,
    UploadProfilePhotoRequest,
)
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChatBannedRights,
)


PREFIXES = (".", ",")
BASE_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = BASE_DIR / "runtime"
DOWNLOAD_DIR = RUNTIME_DIR / "downloads"
STATE_FILE = RUNTIME_DIR / "state.json"
BACKUP_FILE = RUNTIME_DIR / "state.backup.json"
LOG_FILE = RUNTIME_DIR / "userbot.log"

RUNTIME_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)


def configure_logging() -> None:
    """Log to both the console and a bounded local file."""
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=2,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is missing. Add it as a secret.")
    return value


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"autoreplies": {}, "variables": {}, "afk": None}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logging.exception("Could not read state file; starting with empty state.")
        return {"autoreplies": {}, "variables": {}, "afk": None}


def save_state() -> None:
    STATE_FILE.write_text(
        json.dumps(STATE, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def build_client() -> TelegramClient:
    api_id = int(required_env("API_ID"))
    api_hash = required_env("API_HASH")
    session_string = os.getenv("SESSION_STRING", "").strip()
    generating = "--generate-session" in sys.argv

    if session_string:
        return TelegramClient(StringSession(session_string), api_id, api_hash)
    if generating:
        return TelegramClient(StringSession(), api_id, api_hash)
    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        raise RuntimeError(
            "SESSION_STRING is required in GitHub Actions. "
            "Run `python main.py --generate-session` locally first."
        )
    return TelegramClient(os.getenv("SESSION_NAME", "userbot"), api_id, api_hash)


STATE = load_state()
client = build_client()


async def respond(event: events.NewMessage.Event, text: str) -> None:
    """Replace the command message when possible, otherwise reply."""
    text = text[:3900]
    try:
        await event.edit(text)
    except Exception:
        await event.reply(text)


async def replied_user(event: events.NewMessage.Event) -> Any | None:
    message = await event.get_reply_message()
    if not message:
        await respond(event, "Is command ko kisi user ke message par reply karke use karein.")
        return None
    return await message.get_sender()


def safe_variable_name(name: str) -> bool:
    lowered = name.lower()
    blocked_words = ("token", "secret", "password", "hash", "key", "credential")
    return name.replace("_", "").isalnum() and not any(
        word in lowered for word in blocked_words
    )


async def moderation(
    event: events.NewMessage.Event,
    action: str,
) -> None:
    user = await replied_user(event)
    if user is None:
        return

    try:
        if action in {"ban", "unban"}:
            rights = ChatBannedRights(view_messages=action == "ban")
        else:
            muted = action == "mute"
            rights = ChatBannedRights(
                send_messages=muted,
                send_media=muted,
                send_stickers=muted,
                send_gifs=muted,
                send_games=muted,
                send_inline=muted,
                embed_links=muted,
                send_polls=muted,
            )
        await client(EditBannedRequest(event.chat_id, user, rights))
        await respond(event, f"✅ {action.title()} complete.")
    except Exception as exc:
        logging.exception("Moderation command failed")
        await respond(event, f"❌ Moderation failed: {type(exc).__name__}")


async def handle_command(event: events.NewMessage.Event) -> None:
    match = event.pattern_match
    command = match.group(1).lower()
    args = (match.group(2) or "").strip()

    if command in {"help", "h"}:
        await respond(
            event,
            "**Phase 1 commands**\n"
            "`.alive` `.ping` `.usage` `.logs`\n"
            "`.dbbackup` `.dbrestore` `.cleanall` `.refresh`\n"
            "`.ban` `.unban` `.kick` `.mute` `.unmute` `.del` `.purge`\n"
            "`.pin` `.unpin` `.admins`\n"
            "`.setname` `.setbio` `.username` `.setpfp` `.delpfp`\n"
            "`.saved` `.download` `.upload`\n"
            "`.autoreply` `.delreply` `.afk`\n"
            "`.block` `.unblock` `.sendas` `.setvar` `.getvar` `.delvar`\n\n"
            "Advanced commands remain guarded: `.bash`, `.eval`, `.secret`, "
            "`.spy`, unrestricted `.forward`, and voice-chat commands."
        )
        return

    if command == "alive":
        me = await client.get_me()
        name = getattr(me, "username", None) or getattr(me, "first_name", "account")
        await respond(event, f"🟢 Userbot online\nAccount: {name}\nPrefix: . or ,")
        return

    if command == "ping":
        started = asyncio.get_running_loop().time()
        await respond(event, "🏓 Pong!")
        elapsed = (asyncio.get_running_loop().time() - started) * 1000
        await event.edit(f"🏓 Pong! `{elapsed:.0f} ms`")
        return

    if command in {"restart", "shutdown"}:
        if command == "shutdown":
            await respond(event, "🛑 Shutting down.")
            await client.disconnect()
            return
        await respond(event, "🔄 Restarting process.")
        await client.disconnect()
        os.execv(sys.executable, [sys.executable, *sys.argv])
        return

    if command == "update":
        await respond(
            event,
            "ℹ️ Update is controlled by the GitHub Actions workflow. "
            "Push code there and rerun the workflow.",
        )
        return

    if command == "logs":
        try:
            lines = LOG_FILE.read_text(encoding="utf-8").splitlines()[-25:]
            await respond(event, "📋 Recent logs:\n" + ("\n".join(lines) or "No logs yet."))
        except OSError:
            await respond(event, "No logs available.")
        return

    if command in {"usage", "dyno"}:
        load = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0
        disk = shutil.disk_usage(BASE_DIR)
        await respond(
            event,
            f"📊 Load: {load:.2f}\n"
            f"Disk: {disk.used // 1_000_000}/{disk.total // 1_000_000} MB",
        )
        return

    if command == "refresh":
        global STATE
        STATE = load_state()
        await respond(event, "♻️ State and permissions reloaded.")
        return

    if command == "cleanall":
        removed = 0
        for path in DOWNLOAD_DIR.iterdir():
            if path.is_file():
                path.unlink(missing_ok=True)
                removed += 1
        await respond(event, f"🧹 Removed {removed} temporary file(s).")
        return

    if command == "dbbackup":
        shutil.copy2(STATE_FILE, BACKUP_FILE) if STATE_FILE.exists() else save_state()
        await respond(event, f"💾 Backup saved: `{BACKUP_FILE.name}`")
        return

    if command == "dbrestore":
        if not BACKUP_FILE.exists():
            await respond(event, "❌ No database backup exists.")
            return
        shutil.copy2(BACKUP_FILE, STATE_FILE)
        STATE = load_state()
        await respond(event, "✅ State restored from backup.")
        return

    if command in {"ban", "unban", "mute", "unmute"}:
        await moderation(event, command)
        return

    if command == "kick":
        user = await replied_user(event)
        if user is None:
            return
        try:
            await client.kick_participant(event.chat_id, user)
            await respond(event, "✅ User removed.")
        except Exception as exc:
            await respond(event, f"❌ Kick failed: {type(exc).__name__}")
        return

    if command in {"dban", "dmute"}:
        user = await replied_user(event)
        if user is None:
            return
        await moderation(event, "ban" if command == "dban" else "mute")
        message = await event.get_reply_message()
        if message:
            await message.delete()
        return

    if command == "del":
        message = await event.get_reply_message()
        if not message:
            await respond(event, "Reply to a message to delete it.")
            return
        await message.delete()
        await event.delete()
        return

    if command == "purge":
        message = await event.get_reply_message()
        if not message:
            await respond(event, "Reply to the first message to purge from.")
            return
        messages = [
            item async for item in client.iter_messages(
                event.chat_id,
                min_id=message.id - 1,
                max_id=event.id + 1,
                limit=100,
            )
        ]
        if messages:
            await client.delete_messages(event.chat_id, [item.id for item in messages])
        return

    if command in {"pin", "unpin"}:
        message = await event.get_reply_message()
        if not message:
            await respond(event, "Reply to a message first.")
            return
        if command == "pin":
            await client.pin_message(event.chat_id, message, notify=False)
        else:
            await client.unpin_message(event.chat_id, message)
        await respond(event, f"✅ Message {command}ned.")
        return

    if command == "admins":
        admins = await client.get_participants(
            event.chat_id,
            filter=ChannelParticipantsAdmins(),
        )
        names = [getattr(user, "first_name", "unknown") for user in admins[:30]]
        await respond(event, "👮 Admins:\n" + "\n".join(f"• {name}" for name in names))
        return

    if command == "setname":
        parts = args.split(maxsplit=1)
        if not parts:
            await respond(event, "Usage: `.setname <first> [last]`")
            return
        await client(UpdateProfileRequest(first_name=parts[0], last_name=parts[1] if len(parts) > 1 else ""))
        await respond(event, "✅ Display name updated.")
        return

    if command == "setbio":
        await client(UpdateProfileRequest(about=args[:70]))
        await respond(event, "✅ Bio updated.")
        return

    if command == "username":
        username = args.lstrip("@")
        if not username:
            await respond(event, "Usage: `.username <username>`")
            return
        await client(UpdateUsernameRequest(username))
        await respond(event, "✅ Username updated.")
        return

    if command == "setpfp":
        message = await event.get_reply_message()
        if not message or not message.media:
            await respond(event, "Reply to an image to set it as your profile picture.")
            return
        path = await client.download_media(message, file=DOWNLOAD_DIR)
        uploaded = await client.upload_file(path)
        await client(UploadProfilePhotoRequest(file=uploaded))
        Path(path).unlink(missing_ok=True)
        await respond(event, "✅ Profile picture updated.")
        return

    if command in {"delpfp", "countpfp"}:
        photos = await client.get_profile_photos("me", limit=int(args or 100))
        if command == "countpfp":
            await respond(event, f"🖼 Profile pictures: {len(photos)}")
        else:
            if photos:
                await client(DeletePhotosRequest(id=photos))
            await respond(event, f"✅ Deleted {len(photos)} profile picture(s).")
        return

    if command in {"saved", "sv"}:
        message = await event.get_reply_message()
        if not message:
            await respond(event, "Reply to a message to save it.")
            return
        await client.forward_messages("me", message)
        await respond(event, "✅ Saved.")
        return

    if command == "download":
        message = await event.get_reply_message()
        if not message or not message.media:
            await respond(event, "Reply to media to download it.")
            return
        path = await client.download_media(message, file=DOWNLOAD_DIR)
        await respond(event, f"⬇️ Downloaded: `{Path(path).name}`")
        return

    if command == "upload":
        if not args:
            await respond(event, "Usage: `.upload <filename>` from the downloads folder.")
            return
        path = (DOWNLOAD_DIR / args).resolve()
        if DOWNLOAD_DIR.resolve() not in path.parents or not path.is_file():
            await respond(event, "❌ Only files inside runtime/downloads are allowed.")
            return
        await client.send_file(event.chat_id, path)
        await event.delete()
        return

    if command == "autoreply":
        if "|" not in args:
            await respond(event, "Usage: `.autoreply <trigger>|<reply>`")
            return
        trigger, reply = (part.strip() for part in args.split("|", 1))
        STATE["autoreplies"][trigger.lower()] = reply
        save_state()
        await respond(event, "✅ Auto-reply saved.")
        return

    if command == "delreply":
        STATE["autoreplies"].pop(args.lower(), None)
        save_state()
        await respond(event, "✅ Auto-reply removed.")
        return

    if command == "afk":
        STATE["afk"] = args or "away"
        save_state()
        await respond(event, f"💤 AFK enabled: {STATE['afk']}")
        return

    if command in {"block", "unblock"}:
        user = await replied_user(event)
        if user is None:
            return
        request = BlockRequest(user) if command == "block" else UnblockRequest(user)
        await client(request)
        await respond(event, f"✅ User {command}ed.")
        return

    if command == "sendas":
        parts = args.split(maxsplit=1)
        if len(parts) != 2:
            await respond(event, "Usage: `.sendas <chat_id> <text>`")
            return
        await client.send_message(int(parts[0]), parts[1])
        await respond(event, "✅ Message sent.")
        return

    if command in {"setvar", "getvar", "delvar"}:
        parts = args.split(maxsplit=1)
        name = parts[0] if parts else ""
        if not safe_variable_name(name):
            await respond(event, "❌ Invalid or sensitive variable name.")
            return
        if command == "setvar":
            if len(parts) != 2:
                await respond(event, "Usage: `.setvar <name> <value>`")
                return
            STATE["variables"][name] = parts[1]
            save_state()
            await respond(event, "✅ Variable saved.")
        elif command == "getvar":
            await respond(event, f"`{name}` = `{STATE['variables'].get(name, '')}`")
        else:
            STATE["variables"].pop(name, None)
            save_state()
            await respond(event, "✅ Variable removed.")
        return

    if command in {
        "bash",
        "eval",
        "secret",
        "spy",
        "forward",
        "pmpermit",
        "pmpm",
        "allowall",
        "disapproveall",
        "privacy",
        "ghost",
        "zombies",
        "unbanall",
        "muteall",
        "unmuteall",
        "play",
        "vplay",
        "pause",
        "resume",
        "skip",
        "end",
        "queue",
        "volume",
        "shuffle",
        "loop",
        "mutevc",
        "unmutevc",
        "yt",
        "song",
        "vsong",
        "lyrics",
        "kang",
        "tosticker",
        "circle",
        "mirror",
        "packinfo",
    }:
        await respond(
            event,
            "🔒 This advanced command is disabled in the current phase. "
            "It needs an explicit safety review and, where applicable, "
            "additional dependencies or Telegram permissions.",
        )
        return

    await respond(event, f"Unknown command: `{command}`. Use `.help`.")


def _safe_extra_commands():
    """Add additive, non-harmful utility commands without changing existing bot behavior."""
    echo_chats: set[int] = set()

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"^[\.,](calc|reverse|bold|italic|mono|tiny|echo|rmecho|leave|kickme|blocklist|qr|wiki|weather|tr|paste|carbon|readqr|autobio|autoname|privacy|countpfp)\b(?:\s+([\s\S]*))?$",
        )
    )
    async def safe_extra_commands_handler(event: events.NewMessage.Event) -> None:
        command = event.pattern_match.group(1).lower()
        args = (event.pattern_match.group(2) or "").strip()

        if command == "calc":
            try:
                expr = ast.parse(args, mode="eval")
                result = eval(compile(expr, "<calc>", "eval"), {"__builtins__": {}}, {"__import__": __import__})
                await respond(event, f"🧮 `{result}`")
            except Exception as exc:
                await respond(event, f"❌ Calculation error: {type(exc).__name__}")
            raise events.StopPropagation

        if command == "reverse":
            await respond(event, args[::-1])
            raise events.StopPropagation

        if command == "bold":
            await respond(event, "".join(chr(0x1D5D4 + (ord(ch) - 65)) if "A" <= ch <= "Z" else chr(0x1D5EE + (ord(ch) - 97)) if "a" <= ch <= "z" else ch for ch in args))
            raise events.StopPropagation

        if command == "italic":
            await respond(event, "".join(chr(0x1D49C + (ord(ch) - 65)) if "A" <= ch <= "Z" else chr(0x1D4B6 + (ord(ch) - 97)) if "a" <= ch <= "z" else ch for ch in args))
            raise events.StopPropagation

        if command == "mono":
            await respond(event, "".join(chr(0x1D670 + (ord(ch) - 65)) if "A" <= ch <= "Z" else chr(0x1D68A + (ord(ch) - 97)) if "a" <= ch <= "z" else ch for ch in args))
            raise events.StopPropagation

        if command == "tiny":
            tiny_map = str.maketrans({
                "a": "ᵃ", "b": "ᵇ", "c": "ᶜ", "d": "ᵈ", "e": "ᵉ", "f": "ᶠ", "g": "ᵍ", "h": "ʰ", "i": "ⁱ",
                "j": "ʲ", "k": "ᵏ", "l": "ˡ", "m": "ᵐ", "n": "ⁿ", "o": "ᵒ", "p": "ᵖ", "q": "ᑫ", "r": "ʳ",
                "s": "ˢ", "t": "ᵗ", "u": "ᵘ", "v": "ᵛ", "w": "ʷ", "x": "ˣ", "y": "ʸ", "z": "ᶻ",
            })
            await respond(event, args.translate(tiny_map))
            raise events.StopPropagation

        if command == "echo":
            echo_chats.add(event.chat_id)
            await respond(event, "✅ Echo mode enabled for this chat. Use `.rmecho` to disable it.")
            raise events.StopPropagation

        if command == "rmecho":
            echo_chats.discard(event.chat_id)
            await respond(event, "✅ Echo mode disabled.")
            raise events.StopPropagation

        if command in {"leave", "kickme"}:
            if event.is_group:
                await client.delete_dialog(event.chat_id)
                await respond(event, "✅ Left the chat.")
            else:
                await respond(event, "This command works in a group.")
            raise events.StopPropagation

        if command == "blocklist":
            blocked = await client.get_blocked_users()
            lines = [f"• {getattr(user, 'first_name', 'unknown')} (`{user.id}`)" for user in blocked[:20]]
            await respond(event, "🚫 Blocked users:\n" + ("\n".join(lines) or "No blocked users."))
            raise events.StopPropagation

        if command == "qr":
            if not args:
                await respond(event, "Usage: `.qr <text or link>`")
                raise events.StopPropagation
            try:
                import qrcode
                output = DOWNLOAD_DIR / "qr.png"
                qrcode.make(args).save(output)
                await client.send_file(event.chat_id, output, caption="QR code")
                output.unlink(missing_ok=True)
                await event.delete()
            except ImportError:
                await respond(event, "❌ QR support requires `qrcode[pil]`.")
            raise events.StopPropagation

        if command == "wiki":
            if not args:
                await respond(event, "Usage: `.wiki <topic>`")
                raise events.StopPropagation
            await respond(event, "ℹ️ The wiki command is informational-only; configure a wiki API before enabling live lookups.")
            raise events.StopPropagation

        if command == "weather":
            await respond(event, "ℹ️ Weather lookup needs a configured API key and service. It is disabled until you add one.")
            raise events.StopPropagation

        if command == "tr":
            await respond(event, "ℹ️ Translation needs an external API key. It remains disabled until configured.")
            raise events.StopPropagation

        if command in {"paste", "carbon", "readqr", "privacy"}:
            await respond(event, f"ℹ️ `.{command}` is informational-only until its external service is configured.")
            raise events.StopPropagation

        if command in {"autobio", "autoname"}:
            await respond(event, f"ℹ️ `.{command}` is not active yet; use `.setbio` or `.setname` for the safe equivalent.")
            raise events.StopPropagation

        if command == "countpfp":
            photos = await client.get_profile_photos("me", limit=100)
            await respond(event, f"🖼 Profile pictures: {len(photos)}")
            raise events.StopPropagation

    @client.on(events.NewMessage(incoming=True))
    async def echo_repeater(event: events.NewMessage.Event) -> None:
        if event.chat_id in echo_chats and (event.raw_text or "").strip():
            await event.reply(event.raw_text)


_safe_extra_commands()


@client.on(events.NewMessage(outgoing=True, pattern=r"^[\.,](\w+)(?:\s+([\s\S]*))?$") )
async def command_handler(event: events.NewMessage.Event) -> None:
    try:
        await handle_command(event)
    except Exception as exc:
        logging.exception("Command failed")
        await respond(event, f"❌ Command failed: {type(exc).__name__}")


@client.on(events.NewMessage(incoming=True))
async def automation_handler(event: events.NewMessage.Event) -> None:
    """Handle only explicitly configured auto-replies and AFK notices."""
    text = (event.raw_text or "").strip().lower()
    reply = STATE.get("autoreplies", {}).get(text)
    if reply:
        await event.reply(reply)
    if STATE.get("afk") and not event.out:
        await event.reply(f"💤 AFK: {STATE['afk']}")


async def run() -> None:
    if "--generate-session" in sys.argv:
        await client.start()
        print("\nSESSION_STRING=" + client.session.save())
        await client.disconnect()
        return

    await client.start()
    me = await client.get_me()
    logging.info(
        "Userbot online as %s (id=%s)",
        getattr(me, "username", None) or getattr(me, "first_name", "account"),
        me.id,
    )
    await client.run_until_disconnected()


if __name__ == "__main__":
    configure_logging()
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logging.info("Userbot stopped.")
