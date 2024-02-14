import logging
import os
from typing import Optional, Union

from proxmoxer import ProxmoxAPI

from .cache import CacheFor

# @CacheFor(duration=300)  # Cache the API connection for 5 minutes
def get_proxmox_api() -> Optional[ProxmoxAPI]:
    # Move the environment variable reads inside the function to ensure they are evaluated at call time.
    proxmox_url = os.getenv("PROXMOX_URL")
    proxmox_user = os.getenv("PROXMOX_USER")
    proxmox_pass = os.getenv("PROXMOX_PASS")

    if not all([proxmox_url, proxmox_user, proxmox_pass]):
        logging.error("Proxmox API credentials are not set.")
        return None
    return ProxmoxAPI(
        proxmox_url, user=proxmox_user, password=proxmox_pass, verify_ssl=False
    )

def resolve_vm_identifier(
    node_name: str, identifier: Union[str, int]
) -> Optional[Union[int, str]]:
    """Resolve a VM's identifier to its ID or name for operations or information retrieval."""
    logging.debug(
        f"Attempting to resolve VM identifier: {
            identifier} for node: {node_name}"
    )

    proxmox = get_proxmox_api()
    if proxmox is None:
        logging.error("Failed to connect to Proxmox API.")
        return None

    try:
        vms = proxmox.nodes(node_name).qemu.get()
        logging.debug(f"VMs retrieved from node '{node_name}': {vms}")
        for vm in vms:
            logging.debug(f"Checking VM: {vm}")
            if "vmid" not in vm:
                continue
            if isinstance(identifier, int):
                logging.debug(
                    f"Matching identifier as int: {vm['vmid']} == {identifier}"
                )
                if vm["vmid"] == identifier:
                    return vm["vmid"]
            elif isinstance(identifier, str):
                logging.debug(
                    f"Matching identifier as str: {vm['name']} == {
                        identifier} or {vm['vmid']} == {identifier}"
                )
                if vm["name"] == identifier or str(vm["vmid"]) == identifier:
                    return vm["vmid"]
    except Exception as e:
        logging.error(f"Exception occurred in resolve_vm_identifier: {e}")

    logging.debug(f"Could not resolve VM identifier: {identifier}")
    return None
