# README for Discord Proxmox Bot

## Overview

This document provides comprehensive instructions and insights into setting up and running a Discord bot that integrates with Proxmox Virtual Environment (PVE) for managing VMs and providing system information through Discord commands.
![Discord Proxmox Bot](https://i.imgur.com/VjCRZEG.png "Discord Proxmox Bot")

## Prerequisites

- Docker and Docker Compose installed
- Proxmox VE API access
- Discord Bot Token
- Admin Discord User ID

## Configuration

1. **Docker Compose Setup**: Utilize the provided `compose.yml` file to containerize and run the bot. The compose file sets up the necessary environment, including user permissions, environment variables, and volume bindings for the application code.

2. **Environment Variables**: Copy the `.env.example` file to a new file named `.env` and fill in the variables:
    - `PROXMOX_URL`: The URL to your Proxmox VE instance.
    - `PROXMOX_USER`: Proxmox login username (typically `root@pam`).
    - `PROXMOX_PASS`: Proxmox login password.
    - `DISCORD_BOT_TOKEN`: Your Discord Bot Token.
    - `ADMIN_DISCORD_USER_ID`: Discord User ID of the bot admin.

## Running the Bot

Execute the following command in the directory containing your `compose.yml` file:

```sh
docker compose up --build
```

This command builds the Docker image and starts the bot. The bot will automatically restart unless stopped manually.

## Bot Features

- **Admin Commands**: The bot listens for commands from the designated admin user. Commands start with `!` and allow the admin to interact directly with the Proxmox VE API.

- **Proxmox Integration**: Supports various commands to interact with the Proxmox VE API, including:
    - VM management (start, stop, reboot, delete, clone, backup, restore)
    - Snapshot management (create, list, delete, rollback)
    - System information (servers list, VM status, node IP, VM IP)
    - Resource management (resize disk, adjust CPU/memory, list disks)

## Development and Extension

The bot's functionality can be extended by adding new commands or modifying existing ones. Each command is decorated with `@command`.

## Troubleshooting

Ensure all environment variables are correctly set in the `.env` file. Check the Docker and bot logs for any errors. Verify that the bot has the necessary permissions on Discord and that the Proxmox VE API is accessible.
