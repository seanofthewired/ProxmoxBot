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
from command_decorator import command
from transformers import bytes_to_gb
from transformers import vm_info_to_markdown, servers_list_to_markdown, status_to_markdown

@command("Lists all servers in a node", requires_vm_id=False)
def servers(proxmox, node_name: str) -> str:
    logging.info(f"Executing 'servers' command with node name: {node_name}")
    vms = proxmox.nodes(node_name).qemu.get()
    servers_info = []
    for vm in vms:
        vm_name = vm['name']
        vm_id = vm['vmid']
        vm_status = proxmox.nodes(node_name).qemu(vm_id).status.current.get()
        ram_usage = vm_status.get("mem", -1)
        max_ram = vm_status.get("maxmem", -1)
        ram_usage = bytes_to_gb(ram_usage) if ram_usage != -1 else "Error retrieving information"
        max_ram = bytes_to_gb(max_ram) if max_ram != -1 else "Error retrieving information"
        servers_info.append({
            "name": vm_name,
            "vm_id": vm_id,
            "status": vm_status["qmpstatus"],
            "ram_usage": ram_usage,
            "max_ram": max_ram
        })
    return servers_list_to_markdown(servers_info)

@command("Starts a VM if not already running", requires_vm_id=True)
def start(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'start' command with node name: {node_name}, VM ID: {vm_id}")
    proxmox.nodes(node_name).qemu(vm_id).status.start.post()
    return f"Attempting to start VM {vm_id} on node {node_name}."

@command("Stops a VM if it is currently running", requires_vm_id=True)
def stop(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'stop' command with node name: {node_name}, VM ID: {vm_id}")
    proxmox.nodes(node_name).qemu(vm_id).status.stop.post()
    return f"Attempting to stop VM {vm_id} on node {node_name}."

@command("Shows the current status of a VM", requires_vm_id=True)
def status(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'status' command with node name: {node_name}, VM ID: {vm_id}")
    vm_status = proxmox.nodes(node_name).qemu(vm_id).status.current.get()['status']
    return status_to_markdown(vm_status, vm_id)

@command("Shows the current config of a VM", requires_vm_id=True)
def info(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'info' command with node name: {node_name}, VM ID: {vm_id}")
    vm_info = proxmox.nodes(node_name).qemu(vm_id).config.get()
    return vm_info_to_markdown(vm_info)

@command("Creates a snapshot for a VM", requires_vm_id=True)
def create_snapshot(proxmox, node_name: str, vm_id: str, snapshot_name: str) -> str:
    logging.info(f"Creating snapshot '{snapshot_name}' for VM '{vm_id}' on node '{node_name}'")
    try:
        proxmox.nodes(node_name).qemu(vm_id).snapshot.create(snapname=snapshot_name)
        return f"Snapshot '{snapshot_name}' created for VM '{vm_id}'."
    except Exception as e:
        return f"Failed to create snapshot: {str(e)}"

@command("Lists all snapshots for a VM", requires_vm_id=True)
def list_snapshots(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Listing snapshots for VM ID: {vm_id}")
    try:
        snapshots = proxmox.nodes(node_name).qemu(vm_id).snapshot.get()
        if snapshots:
            snapshots_info = "\n".join([f"- {snapshot['name']}" for snapshot in snapshots])
            return f"Snapshots for VM {vm_id}:\n{snapshots_info}"
        else:
            return f"No snapshots found for VM {vm_id}."
    except Exception as e:
        return f"Failed to list snapshots: {str(e)}"

@command("Reboots a VM if it is currently running", requires_vm_id=True)
def reboot(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'reboot' command with node name: {node_name}, VM ID: {vm_id}")
    try:
        proxmox.nodes(node_name).qemu(vm_id).status.reboot.post()
        return f"Rebooting VM {vm_id} on node {node_name}."
    except Exception as e:
        return f"Failed to reboot VM: {str(e)}"

@command("Deletes a VM after explicit confirmation using '--confirmed' parameter", requires_vm_id=True)
def delete_vm(proxmox, node_name: str, vm_id: str, confirmed: str = "") -> str:
    if confirmed != "--confirmed":
        return (f"WARNING: You are about to delete VM {vm_id} on node {node_name}. "
                "This action is irreversible. To confirm, repeat the command with '--confirmed' at the end.")

    logging.info(f"Executing 'delete_vm' command with explicit confirmation for VM ID: {vm_id}")
    try:
        proxmox.nodes(node_name).qemu(vm_id).delete()
        return f"VM {vm_id} has been successfully deleted from node {node_name}."
    except Exception as e:
        return f"Failed to delete VM: {str(e)}"
