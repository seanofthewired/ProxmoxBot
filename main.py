import os
import discord
import logging
from command_handler import handler

logging.basicConfig(level=logging.INFO)

async def send_message(message: discord.Message, user_message: str, is_private: bool) -> None:
    """
    Sends a message to a user or channel based on privacy flag.
    
    :param message: The Discord message object.
    :param user_message: The message content to send.
    :param is_private: Flag indicating if the message should be private.
    """
    try:
        logging.info(f"Preparing to send a message. Private: {is_private}")
        response = handler.respond(user_message)
        if isinstance(response, discord.Embed):
            send_func = message.author.send if is_private else message.channel.send
            await send_func(embed=response)
        else:
            text_response = response if isinstance(response, str) else "An error occurred."
            send_func = message.author.send if is_private else message.channel.send
            await send_func(text_response)
        logging.info("Message sent.")
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