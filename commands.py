import logging
from command_decorator import command
from transformers import bytes_to_gb
from transformers import vm_info_to_markdown, servers_list_to_markdown, status_to_markdown
from session_config import SessionConfig

@command("Lists all servers in a node", requires_vm_id=False, requires_node_name=True)
def servers(proxmox, node_name: str, **kwargs):
    if node_name is None:
        node_name = SessionConfig.get_node()
        if node_name is None:
            return "Node name is required."

    logging.info(f"Executing 'servers' command with node name: {node_name}")
    vms = proxmox.nodes(node_name).qemu.get()
    servers_info = []
    for vm in vms:
        try:
            vm_name = vm.get('name', 'Unknown')
            vm_id = vm.get('vmid', 'Unknown')
            vm_status = proxmox.nodes(node_name).qemu(vm_id).status.current.get()
            ram_usage = vm_status.get("mem", -1)
            max_ram = vm_status.get("maxmem", -1)
            ram_usage = bytes_to_gb(ram_usage) if ram_usage != -1 else "Error retrieving information"
            max_ram = bytes_to_gb(max_ram) if max_ram != -1 else "Error retrieving information"
            servers_info.append({
                "name": vm_name,
                "vm_id": vm_id,
                "status": vm_status.get("qmpstatus", "Unknown"),
                "ram_usage": ram_usage,
                "max_ram": max_ram
            })
        except KeyError as e:
            logging.error(f"Error processing VM data: {e}")
            return "An error occurred while processing VM data."

    return servers_list_to_markdown(servers_info)

@command("Sets the current node name for the session", requires_vm_id=False)
def session_set_node(proxmox, node_name: str) -> str:
    SessionConfig.set_node(node_name)
    return f"Current node set to {node_name}."

@command("Get the current node name for the session", requires_vm_id=False)
def session_get_node(proxmox) -> str:
    node_name = SessionConfig.get_node()
    return f"Current node set to {node_name}."

@command("Starts a VM if not already running")
def vm_start(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'start' command with node name: {node_name}, VM ID: {vm_id}")
    proxmox.nodes(node_name).qemu(vm_id).status.start.post()
    return f"Attempting to start VM {vm_id} on node {node_name}."

@command("Stops a VM if it is currently running")
def vm_stop(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'stop' command with node name: {node_name}, VM ID: {vm_id}")
    proxmox.nodes(node_name).qemu(vm_id).status.stop.post()
    return f"Attempting to stop VM {vm_id} on node {node_name}."

@command("Shows the current status of a VM")
def vm_status(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'status' command with node name: {node_name}, VM ID: {vm_id}")
    vm_status = proxmox.nodes(node_name).qemu(vm_id).status.current.get()['status']
    return status_to_markdown(vm_status, vm_id)

@command("Shows the current config of a VM")
def vm_info(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'info' command with node name: {node_name}, VM ID: {vm_id}")
    vm_info = proxmox.nodes(node_name).qemu(vm_id).config.get()
    return vm_info_to_markdown(vm_info)

@command("Creates a snapshot for a VM")
def snap_create(proxmox, node_name: str, vm_id: str, snapshot_name: str) -> str:
    logging.info(f"Creating snapshot '{snapshot_name}' for VM '{vm_id}' on node '{node_name}'")
    try:
        proxmox.nodes(node_name).qemu(vm_id).snapshot.create(snapname=snapshot_name)
        return f"Snapshot '{snapshot_name}' created for VM '{vm_id}'."
    except Exception as e:
        return f"Failed to create snapshot: {str(e)}"

@command("Lists all snapshots for a VM")
def snap_list(proxmox, node_name: str, vm_id: str) -> str:
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
    
@command("Deletes a snapshot for a VM")
def snap_delete(proxmox, node_name: str, vm_id: str, snapshot_name: str) -> str:
    logging.info(f"Deleting snapshot '{snapshot_name}' for VM '{vm_id}' on node '{node_name}'")
    try:
        proxmox.nodes(node_name).qemu(vm_id).snapshot(snapshot_name).delete()
        return f"Snapshot '{snapshot_name}' deleted for VM '{vm_id}'."
    except Exception as e:
        return f"Failed to delete snapshot: {str(e)}"

@command("Rollbacks a VM to a specified snapshot")
def snap_rollback(proxmox, node_name: str, vm_id: str, snapshot_name: str) -> str:
    logging.info(f"Rolling back VM '{vm_id}' to snapshot '{snapshot_name}' on node '{node_name}'")
    try:
        proxmox.nodes(node_name).qemu(vm_id).snapshot(snapshot_name).rollback.post()
        return f"VM '{vm_id}' rolled back to snapshot '{snapshot_name}'."
    except Exception as e:
        return f"Failed to rollback to snapshot: {str(e)}"
    
@command("Clones a VM, allowing for full or linked clones")
def vm_clone(proxmox, node_name: str, vm_id: str, new_vm_id: str, new_vm_name: str, clone_type: str = "linked") -> str:
    logging.info(f"Cloning VM '{vm_id}' to new VM '{new_vm_id}' on node '{node_name}', Clone type: {clone_type}")
    full_clone = 1 if clone_type.lower() == "full" else 0
    try:
        proxmox.nodes(node_name).qemu(vm_id).clone.create(newid=new_vm_id, name=new_vm_name, full=full_clone)
        clone_type_msg = "full clone" if full_clone else "linked clone"
        return f"VM '{vm_id}' cloned to new VM '{new_vm_id}' as a {clone_type_msg} on node '{node_name}'."
    except Exception as e:
        return f"Failed to clone VM: {str(e)}"

@command("Reboots a VM if it is currently running")
def vm_reboot(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Executing 'reboot' command with node name: {node_name}, VM ID: {vm_id}")
    try:
        proxmox.nodes(node_name).qemu(vm_id).status.reboot.post()
        return f"Rebooting VM {vm_id} on node {node_name}."
    except Exception as e:
        return f"Failed to reboot VM: {str(e)}"

@command("Deletes a VM after explicit confirmation using '--confirmed' parameter")
def vm_delete(proxmox, node_name: str, vm_id: str, confirmed: str = "") -> str:
    if confirmed != "--confirmed":
        return (f"WARNING: You are about to delete VM {vm_id} on node {node_name}. "
                "This action is irreversible. To confirm, repeat the command with '--confirmed' at the end.")

    logging.info(f"Executing 'delete_vm' command with explicit confirmation for VM ID: {vm_id}")
    try:
        proxmox.nodes(node_name).qemu(vm_id).delete()
        return f"VM {vm_id} has been successfully deleted from node {node_name}."
    except Exception as e:
        return f"Failed to delete VM: {str(e)}"
