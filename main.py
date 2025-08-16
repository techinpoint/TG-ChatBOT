import os
import logging
import asyncio
import aiohttp
import discord
from discord import app_commands
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiscordBot(discord.Client):
    """Production-ready Discord bot with OpenRouter integration."""
    
    def __init__(self):
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(intents=intents)
        
        # Initialize command tree
        self.tree = app_commands.CommandTree(self)
        
        # Load environment variables
        self.discord_token = os.getenv('DISCORD_TOKEN')
        self.openrouter_key = os.getenv('OPENROUTER_KEY')
        self.allowed_channel_id = self._get_allowed_channel_id()
        
        # Validate required environment variables
        self._validate_env_vars()
        
        # HTTP session for API calls
        self.session: Optional[aiohttp.ClientSession] = None
        
        logger.info("Discord bot initialized successfully")
    
    def _get_allowed_channel_id(self) -> Optional[int]:
        """Get and validate the allowed channel ID from environment variables."""
        try:
            channel_id_str = os.getenv('ALLOWED_CHANNEL_ID')
            if channel_id_str:
                return int(channel_id_str)
            return None
        except ValueError:
            logger.error("ALLOWED_CHANNEL_ID must be a valid integer")
            return None
    
    def _validate_env_vars(self) -> None:
        """Validate that all required environment variables are set."""
        missing_vars = []
        
        if not self.discord_token:
            missing_vars.append('DISCORD_TOKEN')
        if not self.openrouter_key:
            missing_vars.append('OPENROUTER_KEY')
        if not self.allowed_channel_id:
            missing_vars.append('ALLOWED_CHANNEL_ID')
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    async def setup_hook(self) -> None:
        """Setup hook called when the bot is starting up."""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession()
            
            # Sync slash commands
            await self.tree.sync()
            logger.info(f"Synced {len(self.tree.get_commands())} slash commands")
            
        except Exception as e:
            logger.error(f"Error in setup_hook: {e}")
            raise
    
    async def on_ready(self) -> None:
        """Called when the bot has successfully connected to Discord."""
        logger.info(f"Bot is ready! Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Monitoring channel ID: {self.allowed_channel_id}")
        
        # Set bot status
        activity = discord.Activity(type=discord.ActivityType.listening, name="your messages")
        await self.change_presence(activity=activity)
    
    async def on_disconnect(self) -> None:
        """Called when the bot disconnects from Discord."""
        logger.warning("Bot disconnected from Discord")
    
    async def on_resumed(self) -> None:
        """Called when the bot resumes connection to Discord."""
        logger.info("Bot resumed connection to Discord")
    
    async def on_message(self, message: discord.Message) -> None:
        """Handle incoming messages in the allowed channel."""
        try:
            # Ignore bot messages
            if message.author.bot:
                return
            
            # Check if message is in allowed channel
            if message.channel.id != self.allowed_channel_id:
                return
            
            # Check if message has content
            if not message.content.strip():
                return
            
            logger.info(f"Processing message from {message.author} in {message.channel}: {message.content[:50]}...")
            
            # Send initial thinking message
            thinking_message = await message.channel.send("💭 Thinking...")
            
            try:
                # Get AI response
                ai_response = await self._get_ai_response(message.content)
                
                # Edit the thinking message with the response
                if ai_response:
                    # Split response if it's too long for Discord (2000 char limit)
                    if len(ai_response) > 2000:
                        await thinking_message.edit(content=ai_response[:1997] + "...")
                    else:
                        await thinking_message.edit(content=ai_response)
                else:
                    await thinking_message.edit(content="❌ Sorry, I couldn't generate a response.")
                    
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await thinking_message.edit(content="❌ An error occurred while processing your message.")
                
        except Exception as e:
            logger.error(f"Error in on_message: {e}")
    
    async def _get_ai_response(self, user_message: str) -> Optional[str]:
        """Get response from OpenRouter AI API."""
        if not self.session:
            logger.error("HTTP session not initialized")
            return None
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "meta-llama/llama-3.1-70b-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            async with self.session.post(url, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        ai_message = data['choices'][0]['message']['content']
                        logger.info("Successfully received AI response")
                        return ai_message.strip()
                    else:
                        logger.error("No choices in AI response")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"OpenRouter API error {response.status}: {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("Timeout while calling OpenRouter API")
            return None
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return None
    
    async def close(self) -> None:
        """Clean up resources when the bot is shutting down."""
        if self.session:
            await self.session.close()
        await super().close()
        logger.info("Bot shutdown complete")

# Initialize bot instance
bot = DiscordBot()

# Define slash commands
@bot.tree.command(name="ping", description="Replies with Pong! 🏓")
async def ping_command(interaction: discord.Interaction) -> None:
    """Ping command to test bot responsiveness."""
    try:
        await interaction.response.send_message("Pong! 🏓", ephemeral=True)
        logger.info(f"Ping command used by {interaction.user}")
    except Exception as e:
        logger.error(f"Error in ping command: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ An error occurred", ephemeral=True)

# Error handler for command tree
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    """Handle slash command errors."""
    logger.error(f"Slash command error: {error}")
    
    error_message = "❌ An error occurred while processing your command."
    
    if isinstance(error, app_commands.CommandOnCooldown):
        error_message = f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    elif isinstance(error, app_commands.MissingPermissions):
        error_message = "❌ You don't have permission to use this command."
    elif isinstance(error, app_commands.BotMissingPermissions):
        error_message = "❌ I don't have the required permissions to execute this command."
    
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(error_message, ephemeral=True)
        else:
            await interaction.followup.send(error_message, ephemeral=True)
    except Exception as e:
        logger.error(f"Error sending error message: {e}")

async def main():
    """Main function to run the bot with proper error handling."""
    try:
        logger.info("Starting Discord bot...")
        await bot.start(bot.discord_token)
    except discord.LoginFailure:
        logger.error("Invalid Discord token provided")
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    # Handle graceful shutdown
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")