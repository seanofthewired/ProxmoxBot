import logging
import discord
import urllib3

from .command_handler import handler
from .message_splitter import DiscordMessageSplitter

# Setup logging
logging.basicConfig(level=logging.ERROR)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MessageSender:
    """
    Handles sending messages, abstracting the complexity of dealing with Discord message length limits and splitting logic.
    """
    def __init__(self, client: discord.Client):
        self.client = client

    async def send_message(self, message: discord.Message, user_message: str, is_private: bool) -> None:
        logging.debug(f"Preparing to send a message. Private: {is_private}")
        response = handler.respond(user_message)

        send_func = message.author.send if is_private else message.channel.send

        if isinstance(response, discord.Embed):
            await send_func(embed=response)
        else:
            await self._send_text_response(send_func, response if isinstance(response, str) else "An error occurred.")

    async def _send_text_response(self, send_func, text_response: str):
        splitter = DiscordMessageSplitter()
        chunks = splitter.split_message(text_response)
        for chunk in chunks:
            await send_func(chunk)

class Bot:
    def __init__(self, token: str, admin_id: str):
        self.token = token
        self.admin_id = admin_id
        self.client = discord.Client(intents=self._get_intents())
        self.message_sender = MessageSender(self.client)

        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    async def on_ready(self):
        logging.info(f"{self.client.user} has connected to Discord!")

    async def on_message(self, message: discord.Message):
        if message.author == self.client.user or message.author.bot:
            return

        if str(message.author.id) == self.admin_id and message.content.startswith("!"):
            logging.info(f"Processing admin command: {message.content}")
            await self.message_sender.send_message(message, message.content[1:], is_private=False)

    def _get_intents(self) -> discord.Intents:
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        return intents

    def run(self):
        if not self.token or not self.admin_id:
            logging.error("Token or admin ID not provided.")
            return
        self.client.run(self.token)
