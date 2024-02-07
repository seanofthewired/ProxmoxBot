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

# Constants
BYTES_IN_GIB = 1073741824

def bytes_to_gb(bytes_val: int) -> float:
    """
    Convert bytes to Gigabytes (GiB).

    Args:
        bytes_val (int): Value in bytes to convert.

    Returns:
        float: Value converted to GiB.
    """
    return round(bytes_val / BYTES_IN_GIB, 2)

def vm_info_to_markdown(vm_info: dict) -> str:
    max_key_length = max(len(key) for key in vm_info.keys())
    formatted_string = "```\n"
    for key, value in vm_info.items():
        formatted_value = str(value).replace('\n', ' ')
        formatted_string += f"{key:<{max_key_length}} : {formatted_value}\n"
    formatted_string += "```"
    return formatted_string

def servers_list_to_markdown(servers_info: list) -> str:
    formatted_string = "```\nVM Name          VM ID    Status      RAM Usage\n"
    formatted_string += "-" * 60 + "\n"
    for server in servers_info:
        # Assuming server is a dict with necessary keys
        ram_usage = f"{server['ram_usage']}GB / {server['max_ram']}GB"
        formatted_string += f"{server['name']:<15} {server['vm_id']:<8} {server['status']:<10} {ram_usage}\n"
    formatted_string += "```"
    return formatted_string

def commands_to_markdown(commands_list: list) -> str:
    formatted_string = "```\n"
    for cmd in commands_list:
        formatted_string += f"{cmd['command']} - {cmd['description']}\n"
    formatted_string += "```"
    return formatted_string

def status_to_markdown(status: str, vm_id_or_name: str) -> str:
    return f"```\nVM {vm_id_or_name} is currently {status}.\n```"