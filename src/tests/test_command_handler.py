import pytest
from unittest.mock import patch
from unittest.mock import MagicMock
from bot.command_handler import CommandHandler
from bot.session_config import SessionConfig

@pytest.fixture
def command_handler():
    CommandHandler._instance = None  # Resetting singleton for a clean state
    handler = CommandHandler()
    handler.command_functions = {}
    # Mock command registration
    def dummy_command():
        pass

    handler.register_command('test_group', 'test_command', dummy_command)
    return handler


def test_register_command(command_handler):
    """Test registering a command within a non-default command group."""
    def dummy_command():
        pass
    
    # Register the command within a non-default group
    command_handler.register_command('custom_group', 'test_command', dummy_command)
    assert 'custom_group' in command_handler.command_functions
    assert 'test_command' in command_handler.command_functions['custom_group']

def test_generate_command(command_handler):
    """Test the successful generation of commands and logging."""
    def test_command(param):
        pass
    test_command.__description__ = "A test command"

    command_handler.register_command('test_group', 'test_command', test_command)

    with patch('bot.command_handler.logging') as mock_logging:
        command_handler.generate_commands()
        mock_logging.debug.assert_called_with("Commands generated successfully.")

        # Corrected assertion to match the actual command format that includes the group
        assert any(command["command"] == "test_group test_command <param>" for command in command_handler.commands), \
            f"Command with expected format not found in commands list. Commands: {command_handler.commands}"

def test_generate_command_exception(command_handler):
    """Test the exception handling in generate_commands method."""
    def test_command(param):
        pass

    command_handler.register_command('test_group', 'test_command', test_command)

    with patch('bot.command_handler.logging') as mock_logging, \
         patch('inspect.signature') as mock_signature:
        mock_signature.side_effect = Exception("Test exception")
        command_handler.generate_commands()
        mock_logging.error.assert_called_with(
            "Error generating command for test_group test_command: Test exception"
        )

def test_command_execution_with_group(command_handler):
    # Create a mock command function
    mock_command_function = MagicMock(return_value="Command executed successfully")

    # Manually register the mock command to simulate a real command
    # Assume 'test_group' is a valid command group and 'test_command' is the command you want to test
    command_handler.register_command('test_group', 'test_command', mock_command_function)

    # Simulate sending a command to the `respond` method
    message = 'test_group test_command arg1 arg2'
    response = command_handler.respond(message)

    # Verify that the mock command function was called with the expected arguments
    mock_command_function.assert_called_once_with('arg1', 'arg2')

    # Assert that the response from `respond` is what the mock command function returns
    assert response == "Command executed successfully", "The command execution did not return the expected result."

def test_command_execution_without_group(command_handler):
    # Create a mock command function
    mock_command_function = MagicMock(return_value="Command executed successfully")

    # Manually register the mock command to simulate a real command
    # Assume 'test_group' is a valid command group and 'test_command' is the command you want to test
    command_handler.register_command(None, 'test_command', mock_command_function)

    # Simulate sending a command to the `respond` method
    message = 'test_command arg1 arg2'
    response = command_handler.respond(message)

    # Verify that the mock command function was called with the expected arguments
    mock_command_function.assert_called_once_with('arg1', 'arg2')

    # Assert that the response from `respond` is what the mock command function returns
    assert response == "Command executed successfully", "The command execution did not return the expected result."

def test_parse_command_unexpected_structure(command_handler):
    """Test parsing of command when it does not follow expected structure."""
    # Register a command in the default group for this test
    def dummy_command():
        pass
    command_handler.register_command(None, 'test_command', dummy_command)
    
    # This simulates an unexpected command structure
    parts = ['unexpected_command', 'extra_arg']
    command_group, command, args = command_handler.parse_command(parts)
    
    assert command_group == 'default'
    assert command == 'unexpected_command'
    assert args == ['extra_arg']

def test_generate_help_message_for_group(command_handler):
    """Test generating help message for a specific command group."""
    command_handler.generate_commands()
    help_message = command_handler.generate_help_message('test_group')
    assert 'test_command' in help_message

def test_generate_help_message_for_invalid_group(command_handler):
    """Test generating help message for a specific command group."""
    command_handler.generate_commands()
    help_message = command_handler.generate_help_message('dne')
    assert "No commands found for this group." in help_message

def test_empty_message_response(command_handler):
    """
    Test the response when an empty message is received.
    """
    response = command_handler.respond("")
    assert response == "Please provide a command. Type 'help' for a list of commands.", \
        "Incorrect response for an empty command message."

def test_help_message_response(command_handler):
    """
    Test the response when a 'help' message is requested, ensuring the help
    message accurately reflects registered commands.
    """
    # Register mock commands with descriptions
    def mock_command_one():
        pass
    mock_command_one.__description__ = "Description for mock command one."

    command_handler.register_command('default', 'mock_command_one', mock_command_one)

    # Generate commands and then request help message
    command_handler.generate_commands()
    response = command_handler.respond("help")

    # Check that the help message includes the mock commands and their descriptions
    assert "mock_command_one" in response and "Description for mock command one." in response

def test_help_message_response_with_group(command_handler):
    """
    Test the response when a 'help' message is requested for a specific group,
    ensuring the help message accurately reflects registered commands in that group.
    """
    def mock_command_one():
        pass
    mock_command_one.__description__ = "Description for mock command one."
    def group_command_one():
        pass
    group_command_one.__description__ = "Group command one description."


    command_handler.register_command('default', 'mock_command_one', mock_command_one)
    command_handler.register_command('test_group', 'group_command_one', group_command_one)

    # Generate commands and then request help message for 'test_group'
    command_handler.generate_commands()
    response = command_handler.respond("help test_group")

    # Check that the help message includes only the group commands and their descriptions
    assert "group_command_one" in response and "Group command one description." in response
    # Ensure commands from other groups or default group are not included
    assert "mock_command_one" not in response

def test_exclude_node_name_from_command_description_when_session_config_set(command_handler):
    with patch('bot.command_handler.SessionConfig.get_node', return_value='test_node'):
        def dummy_command(node_name, param1):
            pass
        dummy_command.__description__ = "A command excluding node_name if SessionConfig is set"

        command_handler.register_command('test_group', 'exclude_node_name_command', dummy_command)
        command_handler.generate_commands()

        help_message = command_handler.generate_help_message('test_group')
        
        assert "<node_name>" not in help_message, \
            "The 'node_name' parameter should not be present in the help message when SessionConfig is set."
        
def test_exclude_node_name_from_command_description_when_session_config_not_set(command_handler):
    with patch('bot.command_handler.SessionConfig.get_node', return_value=None):
        def dummy_command(node_name, param1):
            pass
        dummy_command.__description__ = "A command excluding node_name if SessionConfig is set"

        command_handler.register_command('test_group', 'exclude_node_name_command', dummy_command)
        command_handler.generate_commands()

        help_message = command_handler.generate_help_message('test_group')
        
        assert "<node_name>" in help_message, \
            "The 'node_name' parameter should be present in the help message when SessionConfig is not set."

def test_type_error_handling(command_handler):
    """Test that a TypeError in command execution logs an error and returns a message."""
    # Register a command function that will raise a TypeError when called without arguments
    command_handler.register_command('test_group', 'command_with_args', lambda x, y: None)

    # Call the respond method with the command but without required arguments
    result = command_handler.respond("test_group command_with_args")
    
    # Check that the result indicates a usage error
    assert "Incorrect command usage." in result, "TypeError was not handled as expected."

def test_general_exception_handling(command_handler):
    """Test that a general exception in command execution logs an error and returns a message."""
    # Register a command function that will raise a ValueError when called
    def command_that_raises():
        raise ValueError("Intentional error")
    command_handler.register_command('test_group', 'error_command', command_that_raises)

    # Call the respond method with the command that raises an exception
    result = command_handler.respond("test_group error_command")
    
    # Check that the result indicates a generic error
    assert "An error occurred:" in result, "Exception was not handled as expected."

def test_unknown_command_handling(command_handler):
    """Test that an unknown command returns an appropriate message."""
    # Call the respond method with a command that does not exist
    result = command_handler.respond("test_group unknown_command")
    
    # Check that the result indicates the command is unknown
    assert "Unknown command or command group." in result, "Unknown command was not handled as expected."
