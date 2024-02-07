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
