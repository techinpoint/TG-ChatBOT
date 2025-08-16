# Production Discord Bot with OpenRouter Integration

A robust Discord bot that integrates with OpenRouter's AI API to provide intelligent responses in a designated channel.

## Features

- **Slash Commands**: Modern Discord slash command support with `/ping` command
- **AI Integration**: Uses OpenRouter API with Meta-Llama/Llama-3.1-70B-Instruct model
- **Channel-Specific**: Only responds to messages in the configured allowed channel
- **Async Operations**: Non-blocking HTTP requests using aiohttp
- **Production-Ready**: Comprehensive error handling, logging, and reconnection logic
- **Clean Architecture**: Modular, maintainable code structure

## Setup

### 1. Prerequisites

- Python 3.8 or higher
- A Discord application/bot (create at https://discord.com/developers/applications)
- An OpenRouter API key (get from https://openrouter.ai/)

### 2. Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

### 3. Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your environment variables in `.env`:
   ```env
   DISCORD_TOKEN=your_actual_discord_bot_token
   OPENROUTER_KEY=your_actual_openrouter_api_key
   ALLOWED_CHANNEL_ID=your_channel_id_as_integer
   ```

### 4. Discord Bot Setup

1. Go to https://discord.com/developers/applications
2. Create a new application or select an existing one
3. Go to the "Bot" section
4. Copy the bot token and set it as `DISCORD_TOKEN`
5. Enable "Message Content Intent" in the bot settings
6. Invite the bot to your server with appropriate permissions:
   - Send Messages
   - Use Slash Commands
   - Read Message History

### 5. Getting Channel ID

1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click on the desired channel
3. Select "Copy ID"
4. Use this ID as `ALLOWED_CHANNEL_ID`

## Usage

### Running the Bot

```bash
python main.py
```

The bot will:
1. Connect to Discord
2. Sync slash commands
3. Start monitoring the configured channel
4. Log all activities to `bot.log` and console

### Commands

- `/ping` - Test command that replies with "Pong! 🏓"

### Message Processing

When users send messages in the allowed channel:
1. Bot sends "💭 Thinking..." message
2. Sends message content to OpenRouter AI
3. Edits the thinking message with AI response
4. Handles errors gracefully with user-friendly messages

## Architecture

### Key Components

- **DiscordBot Class**: Main bot client with comprehensive error handling
- **Environment Validation**: Ensures all required variables are set
- **Async HTTP Client**: Uses aiohttp for non-blocking API calls
- **Command Tree**: Modern Discord slash command implementation
- **Logging System**: Detailed logging to file and console
- **Graceful Shutdown**: Proper cleanup of resources

### Error Handling

- Network timeouts and retries
- API rate limiting awareness
- Discord connection issues
- Invalid environment variables
- Missing permissions

### Production Features

- **Automatic Reconnection**: Handles Discord disconnections
- **Resource Cleanup**: Properly closes HTTP sessions
- **Comprehensive Logging**: Tracks all operations and errors
- **Memory Efficient**: Async operations prevent blocking
- **Security**: Environment variable-based configuration

## Logs

The bot creates detailed logs in:
- `bot.log` file
- Console output

Monitor these for:
- Connection status
- Message processing
- API errors
- Performance metrics

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Check that `.env` file exists and contains all required variables

2. **"Invalid Discord token"**
   - Verify the bot token is correct
   - Ensure the bot hasn't been regenerated

3. **Bot doesn't respond to messages**
   - Check the channel ID is correct
   - Verify "Message Content Intent" is enabled
   - Ensure bot has permissions in the channel

4. **OpenRouter API errors**
   - Verify API key is valid
   - Check your OpenRouter account credits/limits

### Performance

- Response time depends on OpenRouter API latency (typically 1-5 seconds)
- Bot handles multiple concurrent messages efficiently
- Memory usage remains stable with proper resource management

## Security Notes

- Never commit `.env` file to version control
- Store sensitive tokens securely
- Use environment variables in production
- Regular token rotation is recommended

## License

This project is provided as-is for educational and production use.