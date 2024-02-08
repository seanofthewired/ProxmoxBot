import os
import logging
import functools
from typing import Optional, Union
from proxmoxer import ProxmoxAPI

PROXMOX_URL = os.getenv('PROXMOX_URL')
PROXMOX_USER = os.getenv('PROXMOX_USER')
PROXMOX_PASS = os.getenv('PROXMOX_PASS')

def handle_api_exceptions(func):
    """Decorator to handle exceptions raised by Proxmox API operations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Optional[Union[int, str]]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            return None
    return wrapper

def get_proxmox_api() -> Optional[ProxmoxAPI]:
    if not all([PROXMOX_URL, PROXMOX_USER, PROXMOX_PASS]):
        logging.error("Proxmox API credentials are not set.")
        return None
    return ProxmoxAPI(PROXMOX_URL, user=PROXMOX_USER, password=PROXMOX_PASS, verify_ssl=False)

@handle_api_exceptions
def resolve_vm_identifier(node_name: str, identifier: Union[str, int]) -> Optional[Union[int, str]]:
    """Resolve a VM's identifier to its ID or name for operations or information retrieval."""
    proxmox = get_proxmox_api()
    if proxmox is None:
        return None

    vms = proxmox.nodes(node_name).qemu.get()
    for vm in vms:
        if isinstance(identifier, int) and vm['vmid'] == identifier:
            return vm['vmid']
        elif isinstance(identifier, str) and (vm['name'] == identifier or str(vm['vmid']) == identifier):
            return vm['vmid']
    return None
