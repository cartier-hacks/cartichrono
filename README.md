# Discord TTS Reminder Bot

![screenshot](CartiChrono.png)

A Discord bot that provides recurring text-to-speech reminders in voice channels using Python and the nextcord library.

_A modular Discord bot for voice channel TTS reminders with clean architecture._

## Structure

```
├── master.py              (Main bot file - everything starts here)
├── reminder_cog.py        (Core reminder functionality and slash commands)
├── utils.py              (Audio processing, file management, voice utilities)
├── __init__.py           (Package initialization and exports)
├── .env                  (Environment variables - not tracked in git)
├── .gitignore            (Git ignore rules)
└── requirements.txt      (Python dependencies)
```

## Base Setup

**OS:** NixOS (or any Linux distribution with Python 3.8+)

**Dependencies:** nextcord, gTTS, python-dotenv, asyncio

**Audio Backend:** FFmpeg with PulseAudio support

## Development

`make setup`: Will direnv allow, set up the venv and install dependencies

## Features

Since this is a specialized Discord bot, I built it with specific functionality in mind:

- **Slash Commands:** Modern Discord integration with `/remind`, `/stop_reminder`, and `/list_reminders`
- **TTS Engine:** Google Text-to-Speech (gTTS) with automatic audio conversion
- **Voice Integration:** Seamless connection to Discord voice channels
- **File Management:** Automatic cleanup of temporary audio files
- **Error Handling:** Robust error handling and logging system
- **Multi-Guild Support:** Works across multiple Discord servers

## Bot Commands

- **remind:** Set up recurring TTS reminders (`/remind 30 min "Time for a break!"`)
- **stop_reminder:** Stop your active reminder
- **list_reminders:** View your current active reminders

## System Requirements

**Core Dependencies:**

- **Python:** 3.8+ with asyncio support
- **FFmpeg:** Audio processing and format conversion
- **nextcord:** Modern Discord API wrapper
- **gTTS:** Google Text-to-Speech engine

## Installation

1. **Clone the repository:**

```bash
git clone <your-repo-url>
cd discord-tts-reminder-bot
```

2. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

```bash
# Create .env file with your Discord bot credentials:
DISCORD_TOKEN=your_discord_bot_token_here
MAIN_GUILD_ID=your_main_guild_id_here
```

**Note:** Replace with your actual Discord bot token and main guild ID.

4. **Run the bot:**

```bash
python master.py
```

## Configuration

The bot uses environment variables for sensitive configuration. Create a `.env` file in the root directory:

```env
DISCORD_TOKEN=your_discord_bot_token_here
MAIN_GUILD_ID=your_main_guild_id_here
```

**Important:** Replace the example values with your actual Discord bot token and main guild ID.

**Audio Settings:** The bot automatically converts TTS to 48kHz stereo WAV for optimal Discord compatibility.

**Logging:** All bot activity is logged to `discord.log` with configurable verbosity levels.

## Architecture

**Modular Design:** Clean separation between bot logic, audio processing, and utility functions

**Async/Await:** Full asynchronous operation for handling multiple users and voice connections

**Resource Management:** Automatic cleanup of temporary files and voice connections

## Extra Features

- **Automatic Reconnection:** Handles voice channel disconnections gracefully
- **Multi-User Support:** Each user can have their own independent reminder
- **Guild Prioritization:** Faster command sync to your main Discord server
- **Audio Testing:** Built-in audio playback verification before setting reminders

---

_Built for reliable TTS reminders in Discord voice channels with clean, maintainable code._
