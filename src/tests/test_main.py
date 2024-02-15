import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from discord import Message, Embed, Intents
from bot.main import Bot, MessageSender

@pytest.fixture
def discord_client():
    client = MagicMock()
    client.user = AsyncMock()
    client.user.id = 1234  # Mock bot user ID
    return client

@pytest.fixture
def bot():
    with patch("discord.Client", return_value=MagicMock()):
        with patch("bot.main.Bot._get_intents", return_value=Intents.default()):
            return Bot("dummy_token", "admin_id")

@pytest.fixture
def message_sender(discord_client):
    with patch("discord.Client", return_value=discord_client):
        return MessageSender(discord_client)

@pytest.mark.asyncio
async def test_send_message_private():
    # Setup the client and message sender
    client = MagicMock()
    client.user = AsyncMock()
    client.user.id = 1234

    message_sender = MessageSender(client)

    # Mock the author and message
    author = AsyncMock()
    message = AsyncMock()
    message.author = author
    message.channel = None  # Explicitly showing channel is not used in this test

    # Mock the response from your command handler if necessary
    with patch("bot.main.handler.respond", return_value="Test response"):
        await message_sender.send_message(message, "Test command", True)

    # Verify that author.send was awaited with the expected response
    author.send.assert_awaited_with("Test response")

@pytest.mark.asyncio
async def test_send_message_channel():
    # Setup the client and message sender
    client = MagicMock()
    client.user = AsyncMock()
    client.user.id = 1234

    message_sender = MessageSender(client)

    # Mock the channel and message
    channel = AsyncMock()
    message = AsyncMock()
    message.author = channel  # In this context, pretending author is the channel for simplicity
    message.channel = channel

    # Mock the response from your command handler if necessary
    with patch("bot.main.handler.respond", return_value="Test response"):
        await message_sender.send_message(message, "Test command", False)

    # Verify that channel.send was awaited with the expected response
    channel.send.assert_awaited_with("Test response")

@pytest.mark.asyncio
async def test_send_embed_message(message_sender):
    client = MagicMock()
    client.user = AsyncMock()
    client.user.id = 1234

    message_sender = MessageSender(client)

    # Mock the author, channel, and message
    author = AsyncMock()
    channel = AsyncMock()
    message = AsyncMock()
    message.author = author
    message.channel = channel

    # Create a mock Discord Embed
    embed = Embed(title="Test Embed", description="This is a test embed.")

    # Mock the response from your command handler to return an Embed
    with patch("bot.main.handler.respond", return_value=embed):
        await message_sender.send_message(message, "Test command", False)

    # Verify that channel.send was awaited with the expected embed
    channel.send.assert_awaited_with(embed=embed)

@pytest.mark.asyncio
async def test_on_message_ignore_self(bot, discord_client):
    bot.client.user = AsyncMock()
    bot.client.user.id = 12345
    message = AsyncMock(spec=Message)
    message.author = bot.client.user
    with patch.object(bot.message_sender, "send_message", AsyncMock()) as mock_send:
        await bot.on_message(message)
        mock_send.assert_not_awaited()

@pytest.mark.asyncio
async def test_on_message_process(bot, discord_client):
    message = AsyncMock(spec=Message)
    message.content = "!test"
    message.author.id = "admin_id"
    message.author.bot = False
    with patch.object(bot.message_sender, "send_message", AsyncMock()) as mock_send:
        await bot.on_message(message)
        mock_send.assert_awaited_once()

@pytest.mark.asyncio
async def test_on_ready(bot, discord_client):
    bot.client.user = AsyncMock()
    with patch("logging.info") as mock_log:
        await bot.on_ready()
        mock_log.assert_called_with(f"{bot.client.user} has connected to Discord!")

@pytest.mark.asyncio
async def test_run_missing_token_or_admin_id():
    with patch("discord.Client") as mock_client, \
         patch("logging.error") as mock_log:
        Bot(None, None).run()
        mock_log.assert_called()

def test_bot_run_method(bot):
    # Mock the 'run' method of the discord client within our bot instance
    with patch.object(bot.client, 'run') as mock_run:
        # Attempt to run the bot
        bot.run()

        # Assert that 'run' was called once and with the correct token
        mock_run.assert_called_once_with('dummy_token')