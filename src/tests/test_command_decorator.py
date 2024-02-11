import pytest
import logging
from unittest.mock import MagicMock, patch
from bot.command_decorator import command


# Assuming this mock setup is globally available for all tests
@pytest.fixture(autouse=True)
def mock_dependencies(mocker):
    proxmox_api_mock = MagicMock()
    proxmox_api_mock.nodes.return_value.qemu.get.return_value = [
        {"vmid": 100, "name": "resolved_test_vm"},
    ]
    mocker.patch("bot.command_decorator.get_proxmox_api",
                 return_value=proxmox_api_mock)
    mocker.patch(
        "bot.command_decorator.SessionConfig.get_node", return_value="test_node"
    )

    logging.debug("Applying mock for resolve_vm_identifier")
    mocker.patch(
        "bot.command_decorator.resolve_vm_identifier",
        side_effect=lambda node_name, identifier: (
            100 if identifier == "resolved_test_vm" else None
        ),
    )
    logging.debug("Mock applied")
    return proxmox_api_mock

def test_proxmox_api_injection(mock_dependencies):
    """Test the injection of the mocked Proxmox API object."""

    @command(description="Test API injection")
    def test_func(proxmox_api):
        return proxmox_api

    injected_api = test_func()
    assert (
        injected_api == mock_dependencies
    ), "The proxmox_api object was not injected correctly."
    
def test_proxmox_api_failure(mocker, caplog):
    """Test handling when the Proxmox API is not available."""
    caplog.set_level(logging.ERROR)

    mocker.patch("bot.command_decorator.get_proxmox_api", return_value=None)

    @command(description="Test API failure")
    def test_func(proxmox_api):
        pass

    result = test_func()
    assert "Failed to connect to Proxmox API." in caplog.text
    assert result == "🔴 Failed to connect to Proxmox API."

def test_description_assignment():
    """Test if the function description is correctly assigned."""

    @command(description="Test description")
    def test_func():
        pass

    assert test_func.__description__ == "Test description"

def test_command_grouping():
    """Test command grouping based on function names."""

    @command(description="")
    def network_list_devices():
        pass

    assert (
        network_list_devices.__group__ == "network"
    ), "The function should be grouped under 'network' based on its name prefix"

    @command(description="")
    def listall():
        pass

    assert (
        listall.__group__ == "default"
    ), "The function should be grouped under 'default' when no underscore is present"

def test_default_group_and_command_name_assignment():
    """Ensure that functions are correctly assigned to default groups and command names are set."""

    @command(description="Default group test")
    def foo():
        pass

    assert foo.__group__ == "default", "The function should default to the 'default' group"
    assert foo.__command__ == "foo", "The command name should be set to the function name"

def test_api_injection():
    """Ensure that the Proxmox API is correctly injected into the function."""

    @command(description="")
    def test_function(proxmox_api):
        return proxmox_api

    assert test_function() is not None, "The Proxmox API was not injected into the function."

def test_node_name_injection():
    @command(description="")
    def test_function(proxmox_api, node_name):
        return node_name

    assert test_function() == "test_node", "The node name was not injected into the function."

def test_session_node_not_set_and_missing_node_name(mocker):
    mocker.patch("bot.command_decorator.SessionConfig.get_node", return_value=None)
        
    @command(description="")
    def test_function(proxmox_api, node_name):
        return node_name
    
    assert test_function() == "🔴 TypeError in test_function: missing a required argument: 'node_name'."
    
def test_session_node_set(mocker):
    mocker.patch("bot.command_decorator.SessionConfig.get_node", return_value="pve")
    
    @command(description="")
    def test_function(proxmox_api, node_name):
        return node_name
    
    assert test_function() == "pve", "The session node was not injected into the function."
    
def test_vm_id_resolution_as_kwargs():
    """Ensure VM ID resolution logic properly resolves names to IDs."""

    @command(description="")
    def test_function(proxmox_api, vm_id):
        return vm_id

    resolved_id = test_function(vm_id="resolved_test_vm")
    assert resolved_id == 100, f"Expected VM ID '100', got '{resolved_id}'"

def test_vm_id_resolution_as_positional_args():
    """Ensure VM ID resolution logic properly resolves names to IDs."""

    @command(description="")
    def test_function(proxmox_api, vm_id):
        return vm_id

    resolved_id = test_function("resolved_test_vm")
    assert resolved_id == 100, f"Expected VM ID '100', got '{resolved_id}'"

def test_vm_id_resolution_failure():
    """Ensure VM ID resolution logic properly handles unresolved names."""

    @command(description="")
    def test_function(proxmox_api, vm_id):
        return vm_id

    resolved_id = test_function(vm_id="unresolved_test_vm")
    assert resolved_id == "🔴 Could not resolve VM identifier: unresolved_test_vm", "Expected unresolved VM name"

def test_error_handling():
    """Test error handling for type errors and general exceptions."""

    @command(description="")
    def test_error(proxmox_api, missing_param):
        pass

    result = test_error()
    assert "TypeError" in result

    @command(description="")
    def test_exception(proxmox_api):
        raise Exception("Test exception")

    result = test_exception()
    assert "Test exception" in result