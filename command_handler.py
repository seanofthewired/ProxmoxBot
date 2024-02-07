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

import logging
import inspect
from typing import Callable, List, Dict
from transformers import commands_to_markdown
from commands import *

class CommandHandler:
    """
    A class to manage commands and their execution.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ method to implement singleton pattern.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initialize the CommandHandler.
        """
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.command_functions = {}
            self.logger = logging.getLogger(__name__)
            self.commands = []
            self.register_commands()
            self.generate_commands() 

    def register_commands(self) -> None:
        """
        Automatically register all functions decorated with @command.
        """
        for name, obj in globals().items():
            if inspect.isfunction(obj) and hasattr(obj, "__command__"):
                command_name = getattr(obj, "__command__")
                self.logger.info(f"Registering command: {command_name}")
                self.register_command(command_name, obj)

    def generate_commands(self) -> List[Dict[str, str]]:
        """
        Generate commands array based on registered command functions.

        Returns:
            List[Dict[str, str]]: A list containing dictionaries with command information.
        """
        self.commands.clear()  # Clear existing commands
        logging.info("Generating commands...")
        for command_name, command_func in self.command_functions.items():
            signature = inspect.signature(command_func)
            params = list(signature.parameters.values())[1:]  # Exclude 'self' parameter
            command = f"{command_name} {' '.join([f'<{param.name}>' for param in params])}"
            description = command_func.__description__  # Use function description
            self.commands.append({"command": command, "description": description})
            logging.info(f"Registered command: {command}")
        logging.info("Commands generated successfully.")
        return self.commands

    def register_command(self, command_name: str, func: Callable) -> Callable:
        """
        Register a command function with its corresponding name.

        Args:
            command_name (str): The name of the command.
            func (Callable): The command function.

        Returns:
            Callable: The registered command function.
        """
        self.command_functions[command_name] = func
        return func  # Return the function directly

    def respond(self, message: str) -> str:
        parts = message.split()  # Avoid converting to lowercase to preserve case-sensitive arguments.
        self.logger.info(f"Received message: {message}")

        if not parts:
            self.logger.warning("Empty message received.")
            return "Please provide a command. Type 'help' for a list of commands."

        command = parts[0]

        # Handling the 'help' command as a special case
        if command.lower() == "help":
            self.logger.info("Received 'help' command.")
            return commands_to_markdown(self.commands)

        if len(parts) < 2:  # Ensuring there's at least a command name after excluding 'help'.
            self.logger.warning("Incomplete command received.")
            return "Incomplete command. Type 'help' for a list of commands."

        args = parts[1:]

        if command in self.command_functions:
            command_function = self.command_functions[command]
            try:
                signature = inspect.signature(command_function)
                # Adjusted to consider functions that might only need 'node_name' apart from 'self'
                if len(args) < len(signature.parameters) - 1:  # Excluding 'self' from the count
                    missing_args_count = len(signature.parameters) - 1 - len(args)
                    return f"Missing {missing_args_count} required argument(s)."

                # Dynamically execute the command function with the provided arguments
                return command_function(*args)
            except Exception as e:
                self.logger.error(f"An error occurred while executing {command}: {str(e)}", exc_info=True)
                return f"An error occurred: {str(e)}"
        else:
            self.logger.warning(f"Unknown command: {command}")
            return "Unknown command. Type 'help' for a list of commands."


handler = CommandHandler()