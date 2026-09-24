# Telegram Userbot Commands

**Default prefix:** `.` or `,`  
**Scope:** Owner-only commands unless stated otherwise.

> Use moderation, messaging, and automation commands responsibly. Never expose API keys, tokens, or other secrets.

## System & Bot Control

| Command | Description |
|---|---|
| `.alive` | Check whether the userbot is active and display its details. |
| `.ping` | Check server response time. |
| `.restart` | Restart the userbot. |
| `.update` | Update from the latest GitHub code. |
| `.shutdown` | Shut down the userbot. |
| `.logs` | View background errors and logs. |
| `.usage` / `.dyno` | View server resource usage and load. |
| `.refresh` | Reload modules and permissions without restarting. |
| `.cleanall` | Remove temporary downloads, cached logs, and build files. |
| `.dbbackup` / `.dbrestore` | Create or restore a database backup. |
| `.bash <command>` | Run an authorized Linux command. |
| `.eval <code>` | Evaluate Python code at runtime. |

## Group Administration & Moderation

| Command | Description |
|---|---|
| `.ban` / `.unban` | Ban or unban a user. |
| `.kick` | Remove a member from the group. |
| `.mute` / `.unmute` | Restrict or restore a user's ability to send messages. |
| `.dban` / `.dmute` | Delete the user's message and ban or mute the user. |
| `.pin` / `.unpin` | Pin or unpin a message. |
| `.purge` | Delete messages from the replied message onward. |
| `.del` | Delete a specific message. |
| `.lock <type>` | Restrict media, links, stickers, or another supported type. |
| `.muteall` / `.unmuteall` | Lock or unlock group messaging. |
| `.zombies` | Remove deleted accounts from the group. |
| `.unbanall` | Unban all banned members. |
| `.admins` | Display group administrators. |

## PM Security & Privacy

| Command | Description |
|---|---|
| `.pmpermit on/off` | Enable or disable PM approval protection. |
| `.pmpm` | Toggle PM protection for a specific chat or user. |
| `.a` / `.da` | Approve or disapprove a user. |
| `.allowall` | Approve all pending users. |
| `.disapproveall` | Remove approval from all approved users. |
| `.block` / `.unblock` | Block or unblock a user. |
| `.blocklist` | List blocked users. |
| `.privacy` | Check or manage privacy settings. |
| `.ghost` | Read messages without displaying online or typing status where supported. |

## Profile & Owner Controls

| Command | Description |
|---|---|
| `.setname <first> <last>` | Change the display name. |
| `.setbio <text>` | Change the profile bio. |
| `.setpfp` | Set a replied-to image as the profile picture. |
| `.delpfp <count>` | Delete profile pictures. |
| `.countpfp` | Count profile pictures. |
| `.username <username>` | Change the public username. |
| `.autobio` / `.autoname` | Enable dynamic bio or name updates. |
| `.kickme` / `.leave` | Leave the current group. |
| `.secret` | Display configured secrets only when explicitly required; avoid exposing them. |
| `.setvar <name> <value>` | Set a server configuration variable. |
| `.getvar <name>` / `.delvar <name>` | Read or delete a configuration variable. |
| `.sendas <id> <text>` | Send a message to another chat when authorized. |
| `.saved` / `.sv` | Save a replied-to message to Saved Messages. |

## Automation & Logging

| Command | Description |
|---|---|
| `.autoreply <trigger>|<text>` | Set an automatic reply. |
| `.delreply <trigger>` | Delete an automatic reply. |
| `.snipe on/off` | Enable or disable deleted/edited-message logging. |
| `.spy <username>` | Configure activity tracking where permitted. |
| `.forward <chat_id>` | Route selected incoming messages to another chat. |
| `.afk <reason>` | Set an away status and automatic response. |

## Voice Chat Music

| Command | Description |
|---|---|
| `.play <name>` / `.vplay <name>` | Play audio or audio/video in a voice chat. |
| `.pause` / `.resume` | Pause or resume playback. |
| `.skip` / `.end` | Skip the current track or stop playback. |
| `.queue` | Show the playback queue. |
| `.volume <1-200>` | Set playback volume. |
| `.shuffle` | Randomize the queue. |
| `.loop on/off` | Enable or disable looping. |
| `.mutevc` / `.unmutevc` | Mute or unmute the voice-chat player. |

## Media, Downloads & Stickers

| Command | Description |
|---|---|
| `.download` / `.upload <path>` | Download Telegram media or upload a server file. |
| `.yt <link>` | Download YouTube media. |
| `.song <name>` / `.vsong <name>` | Find and download audio or video. |
| `.lyrics <name>` | Find song lyrics. |
| `.kang` | Add a replied-to image or sticker to a personal pack. |
| `.tosticker` | Convert an image to a sticker. |
| `.circle` | Convert a video to a circular video message. |
| `.mirror` | Create a mirrored copy of supported media. |
| `.packinfo` | Show sticker-pack information. |
| `.ls` / `.rm` / `.ext` | List, remove, or inspect server files. |

## Utilities & Plugins

| Command | Description |
|---|---|
| `.ai <question>` | Ask an AI service a question. |
| `.tr <language>` | Translate text. |
| `.tts <text>` | Convert text to speech. |
| `.weather <city>` | Get weather information. |
| `.calc <expression>` | Calculate an expression. |
| `.wiki <query>` / `.imdb <movie>` | Search Wikipedia or movie information. |
| `.ocr` | Extract text from a replied-to image. |
| `.qr <text-or-link>` / `.readqr` | Create or read a QR code. |
| `.carbon` | Render code or text as an image. |
| `.paste` | Create a paste link for long text. |
| `.q` / `.quotly` | Create a quote sticker from a replied-to message. |
| `.mirror` | Mirror supported media. |

## Text, Fun & Formatting

| Command | Description |
|---|---|
| `.clone <user>` / `.revert` | Copy a profile temporarily or restore the original profile. |
| `.echo <reply>` / `.rmecho` | Enable or disable echo mode. |
| `.spam <count> <text>` | Repeat a message a specified number of times. |
| `.cspam <text>` / `.wspam <text>` | Send each character or word as a separate message. |
| `.delayspam` / `.bigspam` | Send delayed or bulk repeated messages. |
| `.raid <count> <user>` / `.replyraid on/off` | Targeted automated replies; use only with consent. |
| `.hang <count>` | Send repeated messages; avoid abuse or disruption. |
| `.vapor` / `.tiny` / `.reverse` | Apply supported text transformations. |
| `.bold` / `.italic` / `.mono` | Apply text formatting. |
