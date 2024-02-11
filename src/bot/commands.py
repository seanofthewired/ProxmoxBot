import logging
import re

from .command_decorator import command
from .session_config import SessionConfig
from .transformers import (bytes_to_gb, disks_list_to_markdown,
                           servers_list_to_markdown, status_to_markdown,
                           vm_info_to_markdown)


@command("Lists all servers in a node")
def servers(proxmox, node_name: str):
    logging.info(f"Executing 'servers' command with node name: {node_name}")
    vms = proxmox.nodes(node_name).qemu.get()
    servers_info = []
    for vm in vms:
        try:
            vm_name = vm.get("name", "Unknown")
            vm_id = vm.get("vmid", "Unknown")
            vm_status = proxmox.nodes(node_name).qemu(
                vm_id).status.current.get()
            ram_usage = vm_status.get("mem", -1)
            max_ram = vm_status.get("maxmem", -1)
            ram_usage = (
                bytes_to_gb(ram_usage)
                if ram_usage != -1
                else "Error retrieving information"
            )
            max_ram = (
                bytes_to_gb(max_ram)
                if max_ram != -1
                else "Error retrieving information"
            )
            servers_info.append(
                {
                    "name": vm_name,
                    "vm_id": vm_id,
                    "status": vm_status.get("qmpstatus", "Unknown"),
                    "ram_usage": ram_usage,
                    "max_ram": max_ram,
                }
            )

            servers_info.sort(key=lambda x: x["vm_id"])

        except KeyError as e:
            logging.error(f"Error processing VM data: {e}")
            return "An error occurred while processing VM data."

    return servers_list_to_markdown(servers_info)


@command("Sets the current node name for the session")
def session_set_node(proxmox, node_name: str) -> str:
    SessionConfig.set_node(node_name)
    return f"Current node set to {node_name}."


@command("Get the current node name for the session")
def session_get_node(proxmox) -> str:
    node_name = SessionConfig.get_node()
    return f"Current node set to {node_name}."


@command("Starts a VM if not already running")
def vm_start(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(
        f"Executing 'start' command with node name: {
            node_name}, VM ID: {vm_id}"
    )
    proxmox.nodes(node_name).qemu(vm_id).status.start.post()
    return f"Attempting to start VM {vm_id} on node {node_name}."


@command("Stops a VM if it is currently running")
def vm_stop(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(
        f"Executing 'stop' command with node name: {node_name}, VM ID: {vm_id}"
    )
    proxmox.nodes(node_name).qemu(vm_id).status.stop.post()
    return f"Attempting to stop VM {vm_id} on node {node_name}."


@command("Shows the current status of a VM")
def vm_status(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(
        f"Executing 'status' command with node name: {
            node_name}, VM ID: {vm_id}"
    )
    vm_status = proxmox.nodes(node_name).qemu(
        vm_id).status.current.get()["status"]
    return status_to_markdown(vm_status, vm_id)


@command("Shows the current config of a VM")
def vm_info(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(
        f"Executing 'info' command with node name: {node_name}, VM ID: {vm_id}"
    )
    vm_info = proxmox.nodes(node_name).qemu(vm_id).config.get()
    vm_info = {k: vm_info[k] for k in sorted(vm_info)}
    return vm_info_to_markdown(vm_info)


@command("Creates a snapshot for a VM")
def snap_create(proxmox, node_name: str, vm_id: str, snapshot_name: str) -> str:
    logging.info(
        f"Creating snapshot '{snapshot_name}' for VM '{
            vm_id}' on node '{node_name}'"
    )
    proxmox.nodes(node_name).qemu(
        vm_id).snapshot.create(snapname=snapshot_name)
    return f"Snapshot '{snapshot_name}' created for VM '{vm_id}'."


@command("Lists all snapshots for a VM")
def snap_list(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(f"Listing snapshots for VM ID: {vm_id}")
    snapshots = proxmox.nodes(node_name).qemu(vm_id).snapshot.get()
    if snapshots:
        snapshots_info = "\n".join(
            [f"- {snapshot['name']}" for snapshot in snapshots])
        return f"Snapshots for VM {vm_id}:\n{snapshots_info}"
    else:
        return f"No snapshots found for VM {vm_id}."


@command("Deletes a snapshot for a VM")
def snap_delete(proxmox, node_name: str, vm_id: str, snapshot_name: str) -> str:
    logging.info(
        f"Deleting snapshot '{snapshot_name}' for VM '{
            vm_id}' on node '{node_name}'"
    )
    proxmox.nodes(node_name).qemu(vm_id).snapshot(snapshot_name).delete()
    return f"Snapshot '{snapshot_name}' deleted for VM '{vm_id}'."


@command("Rollbacks a VM to a specified snapshot")
def snap_rollback(proxmox, node_name: str, vm_id: str, snapshot_name: str) -> str:
    logging.info(
        f"Rolling back VM '{vm_id}' to snapshot '{
            snapshot_name}' on node '{node_name}'"
    )
    proxmox.nodes(node_name).qemu(vm_id).snapshot(
        snapshot_name).rollback.post()
    return f"VM '{vm_id}' rolled back to snapshot '{snapshot_name}'."


@command("Clones a VM, allowing for full or linked clones")
def vm_clone(
    proxmox,
    node_name: str,
    vm_id: str,
    new_vm_id: str,
    new_vm_name: str,
    clone_type: str = "linked",
) -> str:
    logging.info(
        f"Cloning VM '{vm_id}' to new VM '{new_vm_id}' on node '{
            node_name}', Clone type: {clone_type}"
    )
    full_clone = 1 if clone_type.lower() == "full" else 0
    proxmox.nodes(node_name).qemu(vm_id).clone.create(
        newid=new_vm_id, name=new_vm_name, full=full_clone
    )
    clone_type_msg = "full clone" if full_clone else "linked clone"
    return f"VM '{vm_id}' cloned to new VM '{new_vm_id}' as a {clone_type_msg} on node '{node_name}'."


@command("Reboots a VM if it is currently running")
def vm_reboot(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(
        f"Executing 'reboot' command with node name: {
            node_name}, VM ID: {vm_id}"
    )
    proxmox.nodes(node_name).qemu(vm_id).status.reboot.post()
    return f"Rebooting VM {vm_id} on node {node_name}."


@command("Deletes a VM after explicit confirmation using '--confirmed' parameter")
def vm_delete(proxmox, node_name: str, vm_id: str, confirmed: str = "") -> str:
    if confirmed != "--confirmed":
        return (
            f"WARNING: You are about to delete VM {
                vm_id} on node {node_name}. "
            "This action is irreversible. To confirm, repeat the command with '--confirmed' at the end."
        )

    logging.info(
        f"Executing 'delete_vm' command with explicit confirmation for VM ID: {
            vm_id}"
    )
    proxmox.nodes(node_name).qemu(vm_id).delete()
    return f"VM {vm_id} has been successfully deleted from node {node_name}."


@command("Shows the current IP address of the node")
def node_ip(proxmox, node_name: str) -> str:
    logging.info(f"Fetching current IP address for node '{node_name}'")
    # Fetch node network configuration. Adjust the API call as necessary.
    network_config = proxmox.nodes(node_name).network.get()
    # Find an active network interface with an IP address.
    for iface in network_config:
        if iface.get("address"):
            ip_address = iface["address"]
            return f"The current IP address of node '{node_name}' is {ip_address}."
    return f"Failed to find an active IP address for node '{node_name}'."


@command("Shows the current external IP address of a VM using QEMU Guest Agent")
def vm_ip(proxmox, node_name: str, vm_id: str) -> str:
    logging.info(
        f"Fetching current external IP address for VM '{
            vm_id}' on node '{node_name}'"
    )
    agent_network_info = (
        proxmox.nodes(node_name).qemu(vm_id).agent(
            "network-get-interfaces").get()
    )

    ip_addresses = []
    for iface in agent_network_info.get("result", []):
        for ip_info in iface.get("ip-addresses", []):
            ip_address = ip_info.get("ip-address")
            if ip_info.get("ip-address-type") == "ipv4" and ip_address not in [
                "127.0.0.1"
            ]:
                ip_addresses.append(ip_address)

    if ip_addresses:
        ip_addresses_str = ", ".join(ip_addresses)
        return f"External IP address(es) for VM '{vm_id}' on node '{node_name}': {ip_addresses_str}."
    else:
        return f"No external IP address found for VM '{vm_id}' on node '{node_name}'. Make sure the QEMU Guest Agent is installed and running, and DHCP is enabled."


@command("Lists disks and their sizes for a VM")
def vm_list_disks(proxmox, node_name: str, vm_id: str) -> str:
    # Fetch VM's current configuration
    vm_config = proxmox.nodes(node_name).qemu(vm_id).config.get()

    # Initialize a list to collect disk information
    disks_info = []

    for key, value in vm_config.items():
        if key.startswith(("virtio", "scsi", "ide", "sata")) and not key.startswith(
            "scsihw"
        ):
            # Extract disk size and possibly other details if present
            disk_details = value.split(",")
            disk_size = next(
                (
                    detail.split("=")[1]
                    for detail in disk_details
                    if detail.startswith("size")
                ),
                "Unknown size",
            )
            disks_info.append({"id": key, "size": disk_size})

    # Format the disk information using the new function for better readability
    if disks_info:
        return disks_list_to_markdown(disks_info)
    else:
        return "No disks found for this VM."


@command("Resizes a VM's disk")
def vm_resize_disk(
    proxmox, node_name: str, vm_id: str, disk_id: str, new_size: str
) -> str:
    logging.info(
        f"Attempting to resize disk '{disk_id}' for VM '{
            vm_id}' on node '{node_name}' to {new_size}"
    )

    # Validate new_size format (e.g., '30G' or '1024M')
    if not re.match(r"^\d+(G|M)$", new_size):
        return (
            "Invalid size format. Please specify the new size in gigabytes or megabytes, "
            "e.g., '30G' for 30 GB or '1024M' for 1024 MB."
        )

    resize_result = (
        proxmox.nodes(node_name).qemu(vm_id).resize.put(
            disk=disk_id, size=new_size)
    )

    if resize_result is not None:
        return f"Disk '{disk_id}' for VM '{vm_id}' on node '{node_name}' is being resized to {new_size}."
    else:
        return f"Failed to resize disk '{disk_id}' for VM '{vm_id}'. The operation did not complete successfully."


@command("Starts all VMs on a node")
def vms_start_all(proxmox, node_name: str) -> str:
    vms = proxmox.nodes(node_name).qemu.get()
    for vm in vms:
        proxmox.nodes(node_name).qemu(vm["vmid"]).status.start.post()
    return f"All VMs on node '{node_name}' have been started."


@command("Stops all VMs on a node")
def vms_stop_all(proxmox, node_name: str) -> str:
    vms = proxmox.nodes(node_name).qemu.get()
    for vm in vms:
        proxmox.nodes(node_name).qemu(vm["vmid"]).status.stop.post()
    return f"All VMs on node '{node_name}' have been stopped."


@command("Migrates a VM to another node")
def vm_migrate(proxmox, node_name: str, vm_id: str, target_node: str) -> str:
    proxmox.nodes(node_name).qemu(vm_id).migrate.post(target=target_node)
    return f"VM '{vm_id}' is being migrated from '{node_name}' to '{target_node}'."


@command("Displays CPU and memory usage for a VM")
def vm_stats(proxmox, node_name: str, vm_id: str) -> str:
    stats = proxmox.nodes(node_name).qemu(vm_id).status.current.get()
    cpu_usage = stats.get("cpu", "Unknown")
    mem_usage = stats.get("mem", "Unknown")
    max_mem = stats.get("maxmem", "Unknown")

    # Format the CPU usage as a percentage and round to two decimal places
    cpu_usage_percentage = (
        f"{cpu_usage * 100:.2f}%" if cpu_usage != "Unknown" else "Unknown"
    )

    # Convert memory usage to GB and round to two decimal places
    mem_usage_gb = (
        f"{bytes_to_gb(mem_usage)
                       :.2f} GB" if mem_usage != "Unknown" else "Unknown"
    )
    max_mem_gb = f"{bytes_to_gb(
        max_mem):.2f} GB" if max_mem != "Unknown" else "Unknown"

    vm_info = {
        "VM ID": vm_id,
        "CPU Usage": cpu_usage_percentage,
        "Memory Usage": f"{mem_usage_gb} / {max_mem_gb}",
    }

    return vm_info_to_markdown(vm_info)


@command("Adjusts CPU cores and memory allocation for a VM")
def vm_adjust_resources(
    proxmox, node_name: str, vm_id: str, cpu_cores: str, memory_mb: str
) -> str:
    proxmox.nodes(node_name).qemu(vm_id).config.put(
        cores=cpu_cores, memory=int(memory_mb)
    )
    return (
        f"Resources adjusted for VM {vm_id}: {
            cpu_cores} CPU cores, {memory_mb}MB RAM."
    )


@command("Initiates a backup for a specified VM")
def vm_backup(proxmox, node_name: str, vm_id: str, storage: str, backup_id: str) -> str:
    logging.info(
        f"Initiating backup for VM ID: {vm_id} on storage {
            storage} with backup ID {backup_id}"
    )
    backup_job_id = proxmox.nodes(node_name).vzdump.create(
        vmids=vm_id,
        storage=storage,
        mode="snapshot",
        compress="gzip",
        backup_id=backup_id,
    )
    return (
        f"Backup initiated for VM {vm_id} on storage {
            storage}. Job ID: {backup_job_id}"
    )


@command("Restores a VM from a specified backup")
def vm_restore(proxmox, node_name: str, backup_file: str, storage: str) -> str:
    logging.info(f"Restoring VM from backup file {
                 backup_file} on storage {storage}")
    proxmox.nodes(node_name).storage(
        storage).content.post(volid=backup_file, restore=1)
    return f"VM restoration initiated from backup file {backup_file}."


@command("Lists all backups stored in a specified storage")
def vm_list_backups(proxmox, node_name: str, storage: str, vm_id: str = None) -> str:
    logging.info(
        f"Listing backups for storage: {storage} on node: {
            node_name} for VM ID: {vm_id if vm_id else 'All VMs'}"
    )
    backup_files = proxmox.nodes(node_name).storage(storage).content.get()
    backups_list = []
    for backup in backup_files:
        if backup["content"] == "vzdump" and (
            vm_id is None or (vm_id in backup["volid"])
        ):
            backups_list.append(
                {
                    "volume": backup["volid"],
                    "size": bytes_to_gb(int(backup["size"])),
                    "filename": backup["text"],
                }
            )

    if backups_list:
        return backups_list_to_markdown(backups_list)
    else:
        return (
            f"No backups found for VM ID: {vm_id}"
            if vm_id
            else "No backups found in storage: " + storage
        )
