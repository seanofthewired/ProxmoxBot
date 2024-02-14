import os
import pytest
from unittest.mock import patch, MagicMock, call
from bot.proxmox import get_proxmox_api, resolve_vm_identifier



@pytest.fixture
def mock_get_proxmox_api():
    with patch('bot.proxmox.get_proxmox_api') as mock_get_proxmox_api:
        yield mock_get_proxmox_api

@patch.dict('os.environ', {'PROXMOX_URL': '', 'PROXMOX_USER': '', 'PROXMOX_PASS': ''})
def test_resolve_vm_identifier_no_credentials(mock_get_proxmox_api):
    mock_get_proxmox_api.return_value = None
    result = resolve_vm_identifier("node1", "vm2")
    assert result is None

def test_get_proxmox_api_with_credentials():
    proxmox_url = "https://proxmox.example.com"
    proxmox_user = "user@pam"
    proxmox_pass = "securepassword"
    
    with patch('bot.proxmox.os.getenv') as mock_getenv, \
         patch('bot.proxmox.ProxmoxAPI') as mock_proxmox_api:
        # Setup the mock to return specific values for each environment variable
        mock_getenv.side_effect = lambda var: {
            "PROXMOX_URL": proxmox_url,
            "PROXMOX_USER": proxmox_user,
            "PROXMOX_PASS": proxmox_pass
        }.get(var, None)
        
        # Call the function under test
        result = get_proxmox_api()
        
        # Verify that ProxmoxAPI was called with the mocked environment variables
        mock_proxmox_api.assert_called_once_with(proxmox_url, user=proxmox_user, password=proxmox_pass, verify_ssl=False)
        
        # Verify that the result is indeed an instance of ProxmoxAPI or MagicMock in this context
        assert isinstance(result, MagicMock), "Expected get_proxmox_api to return a ProxmoxAPI instance"

def test_get_proxmox_api_no_credentials():
    with patch('os.getenv', return_value=None) as mock_getenv, \
         patch('bot.proxmox.ProxmoxAPI') as mock_proxmox_api:

        # Calling get_proxmox_api should now return None because
        # the environment variables are all mocked to return None
        result = get_proxmox_api()

        # The ProxmoxAPI should not be called since the credentials are missing
        mock_proxmox_api.assert_not_called()

        # Assert that the result is None
        assert result is None, "Expected get_proxmox_api to return None when credentials are not set"

        # Check that os.getenv was called for each environment variable
        mock_getenv.assert_has_calls([call('PROXMOX_URL'), call('PROXMOX_USER'), call('PROXMOX_PASS')], any_order=True)

def test_resolve_vm_identifier_vms_without_vmid(mock_get_proxmox_api):
    mock_vms = [
        {"name": "vm1"},
        {"vmid": 2, "name": "vm2"},
        {"name": "vm3"}
    ]
    mock_get_proxmox_api.return_value.nodes.return_value.qemu.get.return_value = mock_vms
    result = resolve_vm_identifier("node1", 2)
    assert result == 2  # Should still match the VM with the vmid

def test_resolve_vm_identifier_with_matching_id(mock_get_proxmox_api):
    # Mock the response from the Proxmox API
    mock_vms = [
        {"vmid": 1, "name": "vm1"},
        {"vmid": 2, "name": "vm2"},
        {"vmid": 3, "name": "vm3"}
    ]
    mock_get_proxmox_api.return_value.nodes.return_value.qemu.get.return_value = mock_vms

    # Call the resolve_vm_identifier function with a matching ID
    result = resolve_vm_identifier("node1", 2)

    # Assert that the result is the expected VM ID
    assert result == 2

def test_resolve_vm_identifier_with_matching_name(mock_get_proxmox_api):
    # Mock the response from the Proxmox API
    mock_vms = [
        {"vmid": 1, "name": "vm1"},
        {"vmid": 2, "name": "vm2"},
        {"vmid": 3, "name": "vm3"}
    ]
    mock_get_proxmox_api.return_value.nodes.return_value.qemu.get.return_value = mock_vms

    # Call the resolve_vm_identifier function with a matching name
    result = resolve_vm_identifier("node1", "vm2")

    # Assert that the result is the expected VM ID
    assert result == 2

def test_resolve_vm_identifier_with_non_matching_identifier(mock_get_proxmox_api):
    # Mock the response from the Proxmox API
    mock_vms = [
        {"vmid": 1, "name": "vm1"},
        {"vmid": 2, "name": "vm2"},
        {"vmid": 3, "name": "vm3"}
    ]
    mock_get_proxmox_api.return_value.nodes.return_value.qemu.get.return_value = mock_vms

    # Call the resolve_vm_identifier function with a non-matching identifier
    result = resolve_vm_identifier("node1", 4)

    # Assert that the result is None
    assert result is None

def test_resolve_vm_identifier_with_exception(mock_get_proxmox_api):
    # Mock an exception when calling the Proxmox API
    mock_get_proxmox_api.return_value.nodes.return_value.qemu.get.side_effect = Exception("Test exception")

    # Call the resolve_vm_identifier function
    result = resolve_vm_identifier("node1", 2)

    # Assert that the result is None
    assert result is None