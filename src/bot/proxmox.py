import logging
import os
from typing import Optional, Union

from proxmoxer import ProxmoxAPI

from .cache import cache_for

PROXMOX_URL = os.getenv("PROXMOX_URL")
PROXMOX_USER = os.getenv("PROXMOX_USER")
PROXMOX_PASS = os.getenv("PROXMOX_PASS")


# @cache_for(duration=300)  # Cache the API connection for 5 minutes
def get_proxmox_api() -> Optional[ProxmoxAPI]:
    if not all([PROXMOX_URL, PROXMOX_USER, PROXMOX_PASS]):
        logging.error("Proxmox API credentials are not set.")
        return None
    return ProxmoxAPI(
        PROXMOX_URL, user=PROXMOX_USER, password=PROXMOX_PASS, verify_ssl=False
    )


def resolve_vm_identifier(
    node_name: str, identifier: Union[str, int]
) -> Optional[Union[int, str]]:
    """Resolve a VM's identifier to its ID or name for operations or information retrieval."""
    logging.info(
        f"Attempting to resolve VM identifier: {
            identifier} for node: {node_name}"
    )

    proxmox = get_proxmox_api()
    if proxmox is None:
        logging.error("Failed to connect to Proxmox API.")
        return None

    try:
        vms = proxmox.nodes(node_name).qemu.get()
        logging.info(f"VMs retrieved from node '{node_name}': {vms}")
        for vm in vms:
            logging.info(f"Checking VM: {vm}")
            if "vmid" not in vm:
                logging.warning(f"VM object does not contain 'vmid': {vm}")
                continue
            if isinstance(identifier, int):
                logging.info(
                    f"Matching identifier as int: {vm['vmid']} == {identifier}"
                )
                if vm["vmid"] == identifier:
                    return vm["vmid"]
            elif isinstance(identifier, str):
                logging.info(
                    f"Matching identifier as str: {vm['name']} == {
                        identifier} or {vm['vmid']} == {identifier}"
                )
                if vm["name"] == identifier or str(vm["vmid"]) == identifier:
                    return vm["vmid"]
    except Exception as e:
        logging.error(f"Exception occurred in resolve_vm_identifier: {e}")

    logging.info(f"Could not resolve VM identifier: {identifier}")
    return None
