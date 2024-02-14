import logging
import os

import discord
import urllib3

from .command_handler import handler

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
        logging.info(f"Preparing to send a message. Private: {is_private}")
        response = handler.respond(user_message)

        send_func = message.author.send if is_private else message.channel.send

        if isinstance(response, discord.Embed):
            await send_func(embed=response)
        else:
            await self._send_text_response(send_func, response if isinstance(response, str) else "An error occurred.")

    async def _send_text_response(self, send_func, text_response: str):
        chunks = self._split_message(text_response)
        for chunk in chunks:
            await send_func(chunk)

    def _split_message(self, text_response: str) -> list:
        max_length = 1997  # Discord's max length minus some space for code block syntax
        chunks = []

        while text_response:
            if len(text_response) <= max_length:
                chunks.append(text_response)
                break
            
            # Find the last best split point which could be a space, newline, or outside a code block
            split_point = self._find_split_point(text_response, max_length)

            # Append the chunk up to the split point, taking care of closing and reopening code blocks
            chunks.append(text_response[:split_point])

            # Remove the chunk we just added from the text_response
            text_response = text_response[split_point:]

            # If we're in the middle of a code block, add the closing and opening backticks
            if '```' in text_response and not text_response.startswith('```'):
                if not chunks[-1].endswith('```'):
                    chunks[-1] += '```'  # Close the code block

                # Open a new code block for the remaining text
                chunks.append('```' + text_response)
                text_response = ''  # No more text to process

        return chunks

    def _find_split_point(self, text: str, max_length: int) -> int:
        # If there's a code block that starts before max_length and ends after it, move it entirely to the next chunk
        code_block_start = text.rfind('```', 0, max_length)
        code_block_end = text.find('```', code_block_start + 3)

        if code_block_start != -1 and (code_block_end == -1 or code_block_end > max_length):
            return code_block_start

        # Otherwise, find the last best general split point, preferring to end on a space or newline
        split_point = max_length
        while split_point > 0 and text[split_point] not in ['\n', ' ']:
            split_point -= 1

        # If we couldn't find a better split, default to max_length
        return split_point if split_point > 0 else max_length

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
