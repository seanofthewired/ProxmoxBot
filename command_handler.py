import logging
import inspect
from typing import Callable, List, Dict
from transformers import commands_to_markdown
from commands import *

logging.basicConfig(level=logging.INFO)

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
            self.commands = []
            self.register_commands()
            self.generate_commands() 

    def register_commands(self) -> None:
        for name, obj in globals().items():
            if inspect.isfunction(obj) and hasattr(obj, "__command__"):
                command_name = getattr(obj, "__command__")
                command_group = getattr(obj, "__group__", "default")  # Assume 'default' group if not specified
                logging.info(f"Registering command: {command_group} {command_name}")
                self.register_command(command_group, command_name, obj)


    def generate_commands(self) -> None:
        """
        Generate commands array based on registered command functions.
        """
        self.commands.clear()  # Clear existing commands
        logging.info("Generating commands...")
        for group, commands in self.command_functions.items():
            for command_name, command_func in commands.items():
                try:
                    signature = inspect.signature(command_func)
                    params = list(signature.parameters.values())[2:]  # Exclude 'self' and 'proxmox' parameters
                    command_format = f"{group} {command_name} {' '.join([f'<{param.name}>' for param in params])}"
                    description = command_func.__description__  # Use function description
                    self.commands.append({"command": command_format, "description": description})
                    logging.info(f"Registered command: {command_format}")
                except Exception as e:
                    logging.error(f"Error generating command for {group} {command_name}: {e}")
        logging.info("Commands generated successfully.")

    def register_command(self, command_group: str, command_name: str, func: Callable) -> None:
        """
        Register a command function within a specific command group.

        Args:
            command_group (str): The name of the command group.
            command_name (str): The name of the command.
            func (Callable): The command function to register.
        """
        # Ensure that the command group is set to 'default' if not explicitly specified
        if not command_group:
            command_group = 'default'
        
        # Check if the command group already exists, if not, create it
        if command_group not in self.command_functions:
            self.command_functions[command_group] = {}

        # Register the command within its group
        self.command_functions[command_group][command_name] = func
        logging.info(f"Command '{command_name}' registered under group '{command_group}'")

    def generate_help_message(self, command_group=None):
        global_node_set = SessionConfig.get_node() is not None
        all_groups_info = []

        for group, commands in self.command_functions.items():
            if group == 'default':
                group_name = ''
            else:
                group_name = f"{group} "  # Capitalize group name and add a space
                
            group_commands_info = []
            for cmd, cmd_func in commands.items():
                params = getattr(cmd_func, '__params__', [])
                if global_node_set and 'node_name' in params:
                    params = [param for param in params if param != 'node_name']
                command_format = f"{group_name}{cmd} {' '.join([f'<{param}>' for param in params])}"
                description = getattr(cmd_func, '__description__', 'No description available.')
                group_commands_info.append({"command": command_format.strip(), "description": description})

            formatted_group_commands = commands_to_markdown(group_commands_info)
            all_groups_info.append(formatted_group_commands)

        return "\n".join(all_groups_info)

    def parse_command(self, parts):
        """
        Parses the command string to identify the command group, command, and arguments.

        Args:
            parts (list): The message split into parts [command_group, command, args...]

        Returns:
            tuple: A tuple containing (command_group, command, args)
        """
        logging.info(f"Starting to parse command with parts: {parts}")
        # Initialize default command group
        command_group = 'default'

        # Check if the first part is explicitly specifying a command group
        if parts[0] in self.command_functions and len(parts) > 1:
            command_group = parts[0].lower()
            command = parts[1]
            args = parts[2:]
            logging.info(f"Command group specified. Group: {command_group}, Command: {command}, Args: {args}")
        elif parts[0] in self.command_functions['default']:
            # First part is a command in the default group
            command = parts[0]
            args = parts[1:]
            logging.info(f"Default command group. Command: {command}, Args: {args}")
        else:
            # Handle case where command might not follow expected structure
            command = parts[0]
            args = parts[1:]
            logging.warning(f"Command may not follow expected structure. Interpreted Command: {command}, Args: {args}")

        return command_group, command, args

    def respond(self, message: str) -> str:
        logging.info(f"Received message: {message}")
        parts = message.strip().split()
        
        if not parts:
            logging.warning("No command parts found after splitting message.")
            return "Please provide a command. Type 'help' for a list of commands."
        
        if parts[0].lower() == 'help':
            logging.info("Generating help message.")
            if len(parts) > 1:
                command_group = parts[1].lower()
                if command_group in self.command_functions:
                    return self.generate_help_message(command_group)
                else:
                    return "Unknown command group. Type 'help' for a list of commands."
            else:
                return self.generate_help_message()

        command_group, command, user_args = self.parse_command(parts)
        logging.info(f"Parsed command: Command Group - {command_group}, Command - {command}, User Args - {user_args}")

        if command_group in self.command_functions and command in self.command_functions[command_group]:
            command_function = self.command_functions[command_group][command]
            logging.info(f"Found command function: {command_function}")

            try:
                kwargs = {}
                if hasattr(command_function, 'requires_node_name') and command_function.requires_node_name:
                    if user_args:
                        # Explicitly move 'node_name' from user_args to kwargs
                        kwargs['node_name'] = user_args.pop(0)
                        logging.info(f"'node_name' set to kwargs: {kwargs['node_name']}")
                    else:
                        logging.error("Node name is required but not provided.")
                        return "Node name is required."

                logging.info(f"Final arguments for command function: User Args - {user_args}, Kwargs - {kwargs}")
                result = command_function(*user_args, **kwargs)
                logging.info(f"Command function executed successfully. Result: {result}")
                return result
            except TypeError as e:
                logging.error(f"TypeError when calling {command}: {e}", exc_info=True)
                return "Incorrect command usage. Please check the command format and try again."
            except Exception as e:
                logging.error(f"An error occurred while executing {command_group} {command}: {str(e)}", exc_info=True)
                return f"An error occurred: {str(e)}"
        else:
            logging.warning(f"Unknown command or command group: Command Group - {command_group}, Command - {command}")
            return "Unknown command or command group. Type 'help' for a list of commands."

handler = CommandHandler()
