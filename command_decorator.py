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

import functools
import logging
from proxmox import get_proxmox_api, resolve_vm_identifier

def command(description: str, requires_vm_id=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(node_name: str, vm_id_or_name: str = None, *args, **kwargs):
            try:
                proxmox = get_proxmox_api()
                if proxmox is None:
                    return "Failed to connect to Proxmox."

                if requires_vm_id:
                    vm_id = resolve_vm_identifier(node_name, vm_id_or_name)
                    if not vm_id:
                        return f"VM {vm_id_or_name} not found on node {node_name}."
                    return func(proxmox, node_name, vm_id, *args, **kwargs)
                else:
                    return func(proxmox, node_name, *args, **kwargs)
            except Exception as e:
                logging.error(f"Error in {func.__name__}: {e}")
                return f"An error occurred: {e}"
        wrapper.__description__ = description
        wrapper.__command__ = func.__name__
        return wrapper
    return decorator
