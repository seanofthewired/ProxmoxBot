# ProxmoxBot
Python code that utilizes a Discord bot to read and reply in an assigned text channel. Different prompts will send different API request to a Proxmox server to control Virtual Machines



Responses: This is the logic for how the bot should call the Proxmox class based on what the user typed in a text channel.

DiscordBot: Constructor for the Discord bot. 

Proxmox: The bulk of this class is for generating CSRFPreventionToken and making API calls to the Proxmox server. 

ProxmoxDiscordBot: Main class

