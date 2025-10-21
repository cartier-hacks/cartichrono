import nextcord
from nextcord import Interaction
from nextcord.ext import commands, tasks
import asyncio
import time
import os
from typing import Dict, Any
from utils import AudioUtils

class ReminderManager(commands.Cog):
    """Cog for managing TTS reminders in voice channels"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_reminders: Dict[int, Dict[str, Any]] = {}
        self.reminder_checker.start()
        print("ReminderManager cog initialized")
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.reminder_checker.cancel()
    
    @staticmethod
    def parse_interval(interval_str: str) -> int:
        """Convert interval string like '30 min' to seconds"""
        parts = interval_str.lower().split()
        if len(parts) != 2:
            return None
        
        try:
            number = int(parts[0])
            unit = parts[1]
        except ValueError:
            return None

        if unit in ['min', 'minute', 'minutes']:
            return number * 60
        elif unit in ['hour', 'hours']:
            return number * 3600
        return None
    
    @tasks.loop(seconds=60)
    async def reminder_checker(self):
        """Background task to check and play reminders"""
        current_time = time.time()
        
        for user_id, reminder_data in list(self.active_reminders.items()):
            if current_time >= reminder_data['next_reminder_time']:
                await self._play_reminder(user_id, reminder_data, current_time)
    
    async def _play_reminder(self, user_id: int, reminder_data: Dict[str, Any], current_time: float):
        """Play a reminder for a specific user"""
        print(f"Playing reminder for user {user_id}: '{reminder_data['message']}'")
        
        # Get guild and voice channel
        guild = self.bot.get_guild(reminder_data['guild_id'])
        if not guild:
            print(f"Could not find guild {reminder_data['guild_id']}")
            return
        
        voice_channel = self.bot.get_channel(reminder_data['channel_id'])
        if not voice_channel:
            print(f"Could not find voice channel {reminder_data['channel_id']}")
            return
        
        # Check if audio file still exists
        audio_file = reminder_data['audio_file']
        if not os.path.exists(audio_file):
            print(f"Audio file missing: {audio_file}")
            # Try to recreate the TTS file
            try:
                audio_file = await AudioUtils.create_tts_file(reminder_data['message'], user_id)
                reminder_data['audio_file'] = audio_file
                print(f"Recreated audio file: {audio_file}")
            except Exception as e:
                print(f"Failed to recreate audio file: {e}")
                return
        
        try:
            # Get or create voice client
            voice_client = guild.voice_client
            if not voice_client or not voice_client.is_connected():
                print("Reconnecting to voice channel...")
                if voice_client:
                    await voice_client.disconnect()
                nextcord.VoiceClient.use_ipv6 = False
                voice_client = await voice_channel.connect()
                await asyncio.sleep(1)
            
            # Stop any currently playing audio
            if voice_client.is_playing():
                voice_client.stop()
                await asyncio.sleep(0.5)
            
            #  Create a clean audio source with proper FFmpeg options
            print(f"Creating audio source from: {audio_file}")
            audio_source = nextcord.FFmpegPCMAudio(
                audio_file,
                options='-vn -ar 48000 -ac 2'
            )
            
            # Play the reminder audio
            print("Starting audio playback...")
            voice_client.play(audio_source)
            
            # Wait for audio to finish
            playback_timeout = 30  # Maximum 30 seconds for safety
            start_time = time.time()
            
            while voice_client.is_playing() and (time.time() - start_time) < playback_timeout:
                await asyncio.sleep(0.5)
            
            if voice_client.is_playing():
                print("Audio playback timed out, stopping...")
                voice_client.stop()
            
            # Clean up the audio source object
            try:
                audio_source.cleanup()
            except:
                pass  # Some audio sources don't have cleanup method
            
            print("Audio playback completed")
            
            # Schedule next reminder
            reminder_data['next_reminder_time'] = current_time + reminder_data['interval_seconds']
            
        except Exception as e:
            print(f"Error playing reminder for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
    
    @reminder_checker.before_loop
    async def before_reminder_checker(self):
        """Wait for bot to be ready before starting reminder checker"""
        await self.bot.wait_until_ready()
    
    @nextcord.slash_command(name="remind", description="Set a TTS reminder")
    async def remind(self, interaction: Interaction, interval: str, message: str):
        """Set up a recurring TTS reminder"""
        print(f"Remind command called by {interaction.user.name}")
        
        # DEFER FIRST 
        await interaction.response.defer()
        
        # Parse and validate interval
        interval_seconds = self.parse_interval(interval)
        if interval_seconds is None:
            await interaction.followup.send(
                "Invalid format! Use something like '30 min' or '1 hour'"
            )
            return
        
        # Check if user is in voice channel
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send(
                "You need to be in a voice channel for reminders."
            )
            return
        
        voice_channel = interaction.user.voice.channel
        
        # Connect to voice channel
        try:
            voice_client = await voice_channel.connect(timeout=60.0, reconnect=True)
            print(f"Connected to voice channel: {voice_channel.name}")
            await asyncio.sleep(1)

            # Verify connection
            print(f"Voice client connected: {voice_client.is_connected()}")
            print(f"Voice client channel: {voice_client.channel}")

            #Create TTS audio file
            audio_file = await AudioUtils.create_tts_file(message, interaction.user.id)
            print(f"Audio file ready: {audio_file}")

            # Test Audio Playback
            if not await AudioUtils.test_audio_playback(voice_client, audio_file):
                await interaction.followup.send("Audio Playback test failed")
                return
        
            # Store reminder data
            reminder_data = {
                'channel_id': voice_channel.id,
                'message': message,
                'interval': interval,
                'audio_file': audio_file,
                'user_id': interaction.user.id,
                'interval_seconds': interval_seconds,
                'next_reminder_time': time.time() + interval_seconds,
                'guild_id': interaction.guild.id
            }
            
            self.active_reminders[interaction.user.id] = reminder_data
            
            # ONLY ONE followup message at the end
            await interaction.followup.send(
                f"Reminder set! I'll say '{message}' every '{interval}'"
            )

        except Exception as e:
            await interaction.followup.send(f"Error setting up reminder: {e}")
    
    @nextcord.slash_command(name="stop_reminder", description="Stop your active reminder")
    async def stop_reminder(self, interaction: Interaction):
        """Stop the user's active reminder"""
        user_id = interaction.user.id
        
        if user_id not in self.active_reminders:
            await interaction.response.send_message(
                "You don't have any active reminders.", ephemeral=True
            )
            return
        
        # Remove reminder and clean up audio file
        reminder_data = self.active_reminders.pop(user_id)
        
        # Clean up audio file
        if os.path.exists(reminder_data['audio_file']):
            try:
                os.remove(reminder_data['audio_file'])
            except OSError as e:
                print(f"Failed to remove audio file: {e}")
        
        await interaction.response.send_message(
            f"Stopped your reminder: '{reminder_data['message']}'", ephemeral=True
        )
    
    @nextcord.slash_command(name="list_reminders", description="List your active reminders")
    async def list_reminders(self, interaction: Interaction):
        """Show user's active reminders"""
        user_id = interaction.user.id
        
        if user_id not in self.active_reminders:
            await interaction.response.send_message(
                "You don't have any active reminders.", ephemeral=True
            )
            return
        
        reminder_data = self.active_reminders[user_id]
        next_reminder = reminder_data['next_reminder_time'] - time.time()
        
        if next_reminder > 0:
            minutes_left = int(next_reminder // 60)
            next_reminder_text = f"Next reminder in {minutes_left} minutes"
        else:
            next_reminder_text = "Next reminder due now"
        
        await interaction.response.send_message(
            f"**Active Reminder:**\n"
            f"Message: '{reminder_data['message']}'\n"
            f"Interval: {reminder_data['interval']}\n"
            f"{next_reminder_text}",
            ephemeral=True
        )

def setup(bot):
    """Function to add the cog to the bot"""
    print("Setting up ReminderManager cog")
    bot.add_cog(ReminderManager(bot))
    print("ReminderManager cog added to bot")