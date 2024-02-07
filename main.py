'''
Proxmox VM Manager Bot: A Discord bot for managing Proxmox virtual machines.
Copyright (C) 2024  Brian J. Royer

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact me at: brian.royer@gmail.com or https://github.com/shyce
'''

import os
import discord
import logging
from command_handler import handler

# Set up basic logging
logging.basicConfig(level=logging.INFO)

async def send_message(message: discord.Message, user_message: str, is_private: bool) -> None:
    """
    Sends a message to a user or channel based on privacy flag.
    
    :param message: The Discord message object.
    :param user_message: The message content to send.
    :param is_private: Flag indicating if the message should be private.
    """
    try:
        logging.info(f"Preparing to send a message. Private: {is_private}, User Message: {user_message}")
        response = handler.respond(user_message)
        if is_private:
            await message.author.send(response)
            logging.info("Sent a private message.")
        else:
            await message.channel.send(response)
            logging.info("Sent a public message.")
    except Exception as e:
        logging.error(f"Error sending message: {e}", exc_info=True)

def run_discord_bot() -> None:
    """
    Initializes and runs the Discord bot.
    """
    token = os.getenv('DISCORD_BOT_TOKEN')
    admin_discord_user_id = os.getenv('ADMIN_DISCORD_USER_ID')

    if not token or not admin_discord_user_id:
        logging.error("Token or user ID not found in environment variables.")
        return

    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logging.info(f'{client.user} has connected to Discord!')

    @client.event
    async def on_message(message: discord.Message):
        if message.author == client.user:
            return
        
        if str(message.author.id) == admin_discord_user_id and message.content.startswith('!'):
            logging.info(f"Processing admin command: {message.content}")
            await send_message(
                message,
                message.content[1:],
                is_private=False
            )


    client.run(token)

if __name__ == "__main__":
    run_discord_bot()