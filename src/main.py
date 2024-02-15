import logging
import os
from bot.main import Bot

logging.basicConfig(level=logging.WARNING)

if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    admin_discord_user_id = os.getenv("ADMIN_DISCORD_USER_ID")

    # Ensure that the environment variables are set
    if not token or not admin_discord_user_id:
        print("Environment variables for DISCORD_BOT_TOKEN or ADMIN_DISCORD_USER_ID are missing.")
    else:
        bot = Bot(token, admin_discord_user_id)
        bot.run()
