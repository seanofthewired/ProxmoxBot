import logging
import os

import discord
import urllib3

from .command_handler import handler

logging.basicConfig(level=logging.ERROR)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def send_message(
    message: discord.Message, user_message: str, is_private: bool
) -> None:
    """
    Sends a message to a user or channel based on privacy flag, splitting it into multiple messages if longer than 2000 characters,
    ensuring that code blocks are not improperly split, and avoiding sending empty messages.

    :param message: The Discord message object.
    :param user_message: The message content to send.
    :param is_private: Flag indicating if the message should be private.
    """
    try:
        logging.info(f"Preparing to send a message. Private: {is_private}")
        response = handler.respond(user_message)

        send_func = message.author.send if is_private else message.channel.send

        if isinstance(response, discord.Embed):
            await send_func(embed=response)
        else:
            text_response = (
                response if isinstance(response, str) else "An error occurred."
            )
            chunks = []

            while text_response:
                # Limit to 2000 characters, taking care not to split inside code blocks
                split_point = 1997  # Reserve space for closing code block if needed
                if len(text_response) > split_point:
                    # Attempt to avoid splitting inside a code block
                    last_code_block_end = text_response.rfind(
                        "```", 0, split_point)
                    next_code_block_start = text_response.find(
                        "```", last_code_block_end + 3
                    )
                    # If we're starting inside a code block, find the end of it
                    if (
                        next_code_block_start != -1
                        and next_code_block_start < split_point
                    ):
                        split_point = next_code_block_start
                    # Otherwise, try to find a newline to split on
                    else:
                        last_newline = text_response.rfind(
                            "\n", 0, split_point)
                        if last_newline != -1:
                            split_point = last_newline + 1

                chunk, text_response = (
                    text_response[:split_point],
                    text_response[split_point:],
                )
                if chunk:  # Ensure we don't attempt to send empty chunks
                    chunks.append(chunk)

            # Send each chunk as a separate message
            for chunk in chunks:
                await send_func(chunk)

        logging.info("Message(s) sent.")
    except Exception as e:
        logging.error(f"Error sending message: {e}", exc_info=True)


def run() -> None:
    """
    Initializes and runs the Discord bot.
    """
    token = os.getenv("DISCORD_BOT_TOKEN")
    admin_discord_user_id = os.getenv("ADMIN_DISCORD_USER_ID")

    if not token or not admin_discord_user_id:
        logging.error("Token or user ID not found in environment variables.")
        return

    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logging.info(f"{client.user} has connected to Discord!")

    @client.event
    async def on_message(message: discord.Message):
        if message.author == client.user:
            return

        if str(
            message.author.id
        ) == admin_discord_user_id and message.content.startswith("!"):
            logging.info(f"Processing admin command: {message.content}")
            await send_message(message, message.content[1:], is_private=False)

    client.run(token)


if __name__ == "__main__":
    run()
