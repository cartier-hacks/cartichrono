import nextcord
from gtts import gTTS
import subprocess
import os
import asyncio
from typing import Optional

class AudioUtils:
    """Utility class for audio processing and TTS functionality"""
    
    @staticmethod
    async def create_tts_file(text: str, user_id: int) -> str:
        """Create TTS audio file and convert to Discord-compatible format"""
        # Create TTS file

        tts = gTTS(text=text, lang='en', slow=False)
        mp3_file = f"reminder_{user_id}.mp3"
        tts.save(mp3_file)
        
        # Convert to WAV for better Discord compatibility

        wav_file = f"reminder_{user_id}.wav"
        try:
            subprocess.run([
                'ffmpeg', '-i', mp3_file, '-ar', '48000', '-ac', '2', wav_file, '-y'
            ], capture_output=True, check=True)
            
            # Clean up MP3 file

            if os.path.exists(mp3_file):
                os.remove(mp3_file)
                
            return wav_file
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg conversion failed: {e}")
            return mp3_file  # Fall back to MP3 if WAV conversion fails
    
    @staticmethod
    async def test_audio_playback(voice_client, audio_file: str) -> bool:
        """Test if audio can be played through the voice client"""
        try:
            # Use same clean FFmpeg options as in the main playback
            test_source = nextcord.FFmpegPCMAudio(
                audio_file, 
                options='-vn -ar 48000 -ac 2'  # Consistent with main playback
            )
            voice_client.play(test_source)
            
            # Wait a moment for playback to start

            await asyncio.sleep(0.5)
            
            if not voice_client.is_playing():
                print("Audio failed to start playing")
                return False
            
            # Wait for audio to finish

            while voice_client.is_playing():
                await asyncio.sleep(0.5)
            
            # Clean up the test audio source
            try:
                test_source.cleanup()
            except:
                pass  # Some audio sources don't have cleanup method
            
            print("Audio test completed successfully")
            return True
            
        except Exception as e:
            print(f"Audio test failed: {e}")
            return False
    
    @staticmethod
    async def test_ffmpeg_installation() -> dict:
        """Test FFmpeg installation and audio format support"""
        tests = [
            (['ffmpeg', '-version'], "FFmpeg version"),
            (['ffmpeg', '-codecs'], "Codec support"),
            (['ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=1', '-f', 'null', '-'], "Audio generation test"),
        ]
        
        results = {}
        for cmd, name in tests:
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=10)
                results[name] = result.returncode == 0
            except Exception as e:
                results[name] = False
                
        return results

class FileManager:
    """Utility class for file management operations"""
    
    @staticmethod
    def cleanup_audio_file(file_path: str) -> bool:
        """Safely remove an audio file"""
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up audio file: {file_path}")
                return True
            except OSError as e:
                print(f"Failed to remove audio file {file_path}: {e}")
                return False
        return True
    
    @staticmethod
    def cleanup_old_files(pattern: str = "reminder_*.wav", max_age_hours: int = 24):
        """Clean up old audio files based on age"""
        import glob
        import time
        
        current_time = time.time()
        files_removed = 0
        
        for file_path in glob.glob(pattern):
            try:
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > (max_age_hours * 3600):  # Convert hours to seconds
                    os.remove(file_path)
                    files_removed += 1
                    print(f"Removed old file: {file_path}")
            except OSError as e:
                print(f"Failed to remove old file {file_path}: {e}")
        
        if files_removed > 0:
            print(f"Cleaned up {files_removed} old audio files")

class VoiceUtils:
    """Utility class for Discord voice operations"""
    
    @staticmethod
    async def ensure_voice_connection(guild, voice_channel, max_retries: int = 3) -> Optional[nextcord.VoiceClient]:
        """Ensure a stable voice connection with retries"""
        voice_client = guild.voice_client
        
        # If already connected and working, return existing client

        if voice_client and voice_client.is_connected():
            return voice_client
        
        # Attempt to connect with retries

        for attempt in range(max_retries):
            try:
                if voice_client:
                    await voice_client.disconnect()
                
                voice_client = await voice_channel.connect()
                await asyncio.sleep(1)  # Give connection time to establish
                
                if voice_client.is_connected():
                    print(f"Successfully connected to voice channel (attempt {attempt + 1})")
                    return voice_client
                else:
                    print(f"Connection attempt {attempt + 1} failed - not connected")
                    
            except Exception as e:
                print(f"Voice connection attempt {attempt + 1} failed: {e}")
                
            # Wait before retry
            
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
        
        print(f"Failed to establish voice connection after {max_retries} attempts")
        return None
    
    @staticmethod
    async def safe_disconnect(voice_client) -> bool:
        """Safely disconnect from voice channel"""
        if not voice_client:
            return True
            
        try:
            await voice_client.disconnect()
            return True
        except Exception as e:
            print(f"Error disconnecting from voice: {e}")
            return False