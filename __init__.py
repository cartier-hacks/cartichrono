# Discord TTS Reminder Bot
# A Discord bot that provides recurring text-to-speech reminders in voice channels

__version__ = "1.0.0"
__author__ = "cartierhacks"
__description__ = "Discord Reminder Bot with Recurring TTS"

from .reminder_cog import ReminderManager
from .utils import AudioUtils, FileManager, VoiceUtils

__all__ = [
    "ReminderManager",
    "AudioUtils", 
    "FileManager",
    "VoiceUtils"
]