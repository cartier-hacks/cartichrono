import nextcord
from nextcord.ext import commands
#import logging
import os
import asyncio
from dotenv import load_dotenv
from utils import FileManager

class ReminderBot(commands.Bot):
    """Discord TTS Reminder Bot - Main bot class"""
    
    def __init__(self):
        # Set up intents
        intents = nextcord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix='!', 
            intents=intents,
            help_command=None
        )
        
        #self.setup_logging()
    
    #def setup_logging(self):
        #"""Configure logging for the bot"""
        #handler = logging.FileHandler(
            #filename='discord.log', 
            #encoding='utf-8', 
            #mode='w'
        #)
        
        #logging.basicConfig(
            #handlers=[handler],
            #level=logging.INFO,
            #format='%(asctime)s:%(levelname)s:%(name)s: %(message)s'
        #)
        
        # Reduce nextcord logging verbosity
        #logging.getLogger('nextcord').setLevel(logging.WARNING)
        #logging.getLogger('nextcord.http').setLevel(logging.WARNING)
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        print("setup_hook() called - starting setup")
        
        # Clean up old audio files on startup
        FileManager.cleanup_old_files()
        
        # Load cogs here - BEFORE the bot is ready
        try:
            print("About to load reminder_cog extension...")
            
            # Check if the file exists
            if os.path.exists('reminder_cog.py'):
                print("reminder_cog.py file found")
            else:
                print("ERROR: reminder_cog.py file not found!")
                return
                
            await self.load_extension('reminder_cog')
            print("Successfully loaded reminder_cog in setup_hook")
            print(f"Cogs after loading: {list(self.cogs.keys())}")
        except Exception as e:
            print(f"Failed to load reminder_cog: {e}")
            import traceback
            traceback.print_exc()
    
    async def on_ready(self):
        """Called when bot is ready"""
        print(f"\nBot ready! Logged in as {self.user}")
        print(f"Connected to {len(self.guilds)} guilds")
        print(f"Serving {sum(guild.member_count for guild in self.guilds)} users")
        print("=" * 50)

        for guild in self.guilds:
            print(f" - {guild.name} (ID: {guild.id})")
        
        # Try loading the cog here if setup_hook didn't work
        if not self.cogs:
            print("No cogs loaded, trying to load reminder_cog now...")
            try:
                if os.path.exists('reminder_cog.py'):
                    print("reminder_cog.py file found")
                else:
                    print("ERROR: reminder_cog.py file not found!")
                
                await self.load_extension('reminder_cog')
                print("Successfully loaded reminder_cog in on_ready")
            except Exception as e:
                print(f"Failed to load reminder_cog in on_ready: {e}")
                import traceback
                traceback.print_exc()
        
        # Check if commands are loaded
        print(f"Loaded cogs: {list(self.cogs.keys())}")
        print(f"Available slash commands: {[cmd.name for cmd in self.get_all_application_commands()]}")
        
        # Wait a moment for commands to fully register
        await asyncio.sleep(2)
        
        # Try guild sync first (instant) then global sync
        try:
            # Sync to specific server first (instant)
            your_guild_id_str = os.getenv('MAIN_GUILD_ID')
            if not your_guild_id_str:
                print("MAIN_GUILD_ID not found in environment variables - skipping main guild sync")
                your_guild_id = None
            else:
                your_guild_id = int(your_guild_id_str)
            
            if your_guild_id:
                your_guild = self.get_guild(your_guild_id)
                if your_guild:
                    synced_main = await self.sync_application_commands(guild_id=your_guild_id)
                    if synced_main:
                        print(f"Synced {len(synced_main)} commands to your main server: {your_guild.name}")
                    else:
                        print(f"Sync returned None for your main server: {your_guild.name}")
                else:
                    print(f"Could not find guild with ID {your_guild_id}")
            
            # Sync to all other guilds too
            for guild in self.guilds:
                if not your_guild_id or guild.id != your_guild_id:
                    try:
                        synced_guild = await self.sync_application_commands(guild_id=guild.id)
                        if synced_guild:
                            print(f"Synced {len(synced_guild)} commands to guild: {guild.name}")
                        else:
                            print(f"Sync returned None for guild: {guild.name}")
                    except Exception as e:
                        print(f"Failed to sync to guild {guild.name}: {e}")
            
            # Also sync globally (takes up to 1 hour to appear)
            synced_global = await self.sync_all_application_commands()
            if synced_global:
                print(f"Synced {len(synced_global)} global slash commands")
            else:
                print("Global sync returned None")
            
            print("Command sync process completed!")
            print("Check your Discord server - commands should appear now!")
                    
        except Exception as e:
            print(f"Failed to sync commands: {e}")
            import traceback
            traceback.print_exc()

        print("Bot is ready and operational!")
        print("=" * 50)
        
        import subprocess
        print("="*50)
        print("Checking FFmpeg installation...")
        try:
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            print(f"FFmpeg location: {result.stdout.strip()}")

            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            print(f"FFmpeg version: {result.stdout.split('version')[1].split()[0] if 'version' in result.stdout else 'unknown'}")
        except Exception as e:
            print(f"ERROR: FFmpeg check failed: {e}")
        print("="*50)
    
    async def on_application_command_error(self, interaction, error):
        """Handle slash command errors"""
        print(f"Command error: {error}")
        print(f"Command: {interaction.data}")
        print(f"User: {interaction.user}")
        print(f"Guild: {interaction.guild}")
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"An error occurred: {error}", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"An error occurred: {error}", ephemeral=True
                )
        except Exception as e:
            print(f"Failed to send error message: {e}")
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        print(f"Joined new guild: {guild.name} (ID: {guild.id})")
    
    async def on_guild_remove(self, guild):
        """Called when bot is removed from a guild"""
        print(f"Removed from guild: {guild.name} (ID: {guild.id})")
    
    async def close(self):
        """Clean up when bot is shutting down"""
        print("Bot shutting down...")
        FileManager.cleanup_old_files(max_age_hours=0)
        await super().close()

def main():
    """Main function to run the bot"""
    # Load environment variables
    load_dotenv()
    
    # Get Discord token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables")
        print("Please create a .env file with your Discord bot token:")
        print("DISCORD_TOKEN=your_bot_token_here")
        return
    
    # Create and run bot
    bot = ReminderBot()
    
    try:
        print("Starting Discord TTS Reminder Bot...")
        bot.run(token)
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Failed to run bot: {e}")
    finally:
        print("Bot shutdown complete.")

if __name__ == "__main__":
    main()