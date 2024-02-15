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
    formatted_string = "```markdown\n"
    for key, value in vm_info.items():
        formatted_value = str(value).replace("\n", " ")
        formatted_string += f"[{key:<{max_key_length}}]:\t{formatted_value}\n"
    formatted_string += "```"
    return formatted_string


def servers_list_to_markdown(servers_info: list) -> str:
    max_name_length = max(len(server["name"]) for server in servers_info) + 2
    max_id_length = max(len(str(server["vm_id"]))
                        for server in servers_info) + 2

    formatted_string = "```markdown\n"
    formatted_string += (
        f"On \t{'Name':{max_name_length}}\t{'ID':{max_id_length}}\tRAM\n"
    )
    formatted_string += "-" * (max_name_length + max_id_length + 35) + "\n"

    for server in servers_info:
        status = "🟢 " if server["status"].lower() == "running" else "🔴 "
        ram_usage = f"{server['ram_usage']
            :.2f} GB / {server['max_ram']:.2f} GB"
        formatted_string += f"{status}\t{server['name']:{max_name_length}}\t{
            str(server['vm_id']):{max_id_length}}\t{ram_usage}\n"

    formatted_string += "```"
    return formatted_string


def commands_to_markdown(commands_list: list) -> str:
    formatted_string = "```markdown\n"
    for cmd in commands_list:
        formatted_string += f"{cmd['command']} - {cmd['description']}\n"
    formatted_string += "```"
    return formatted_string


def disks_list_to_markdown(disks_info: list) -> str:
    if not disks_info:
        return "```No disks found.```"

    max_disk_id_length = max(len(disk["id"]) for disk in disks_info) + 2
    max_size_length = max(len(disk["size"]) for disk in disks_info) + 2

    formatted_string = "```markdown\n"
    formatted_string += (
        f"{'Disk ID':{max_disk_id_length}}\t{'Size':{max_size_length}}\n"
    )
    formatted_string += "-" * (max_disk_id_length + max_size_length + 5) + "\n"

    for disk in disks_info:
        formatted_string += (
            f"{disk['id']:{max_disk_id_length}}\t{
                disk['size']:{max_size_length}}\n"
        )

    formatted_string += "```"
    return formatted_string


def status_to_markdown(status: str, vm_id_or_name: str) -> str:
    return f"```\nVM {vm_id_or_name} is currently {status}.\n```"


def backups_list_to_markdown(backups_list: list) -> str:
    formatted_string = "```markdown\n"
    formatted_string += "Backups:\n"
    formatted_string += "-" * 20 + "\n"
    for backup in backups_list:
        formatted_string += f"Volume: {backup['volume']}, Size: {
            backup['size']} GB, Filename: {backup['filename']}\n"
    formatted_string += "```"
    return formatted_string
