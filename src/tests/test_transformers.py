import pytest
from unittest.mock import patch
from bot.transformers import bytes_to_gb, vm_info_to_markdown, servers_list_to_markdown, commands_to_markdown, disks_list_to_markdown, status_to_markdown, backups_list_to_markdown

def test_bytes_to_gb():
    assert bytes_to_gb(1073741824) == 1.0
    assert bytes_to_gb(0) == 0
    assert bytes_to_gb(2147483648) == 2.0

def test_vm_info_to_markdown():
    vm_info = {
        "Name": "TestVM",
        "Status": "Running",
        "IP": "192.168.1.1"
    }
    expected_md = """```markdown
[Name  ]:\tTestVM
[Status]:\tRunning
[IP    ]:\t192.168.1.1
```"""
    assert vm_info_to_markdown(vm_info) == expected_md

def test_servers_list_to_markdown():
    servers_info = [
        {"name": "Server1", "vm_id": "1", "status": "running", "ram_usage": 2.0, "max_ram": 4.0},
        {"name": "Server2", "vm_id": "2", "status": "stopped", "ram_usage": 1.5, "max_ram": 3.0}
    ]
    expected_md = """```markdown
On \tName     \tID \tRAM
-----------------------------------------------
🟢 \tServer1  \t1  \t2.00 GB / 4.00 GB
🔴 \tServer2  \t2  \t1.50 GB / 3.00 GB
```"""
    assert servers_list_to_markdown(servers_info) == expected_md

def test_commands_to_markdown():
    commands_list = [
        {"command": "ls", "description": "List directory contents"},
        {"command": "cd", "description": "Change directory"}
    ]
    expected_md = """```markdown
ls - List directory contents
cd - Change directory
```"""
    assert commands_to_markdown(commands_list) == expected_md

def test_disks_list_to_markdown():
    disks_info = [
        {"id": "disk1", "size": "100 GB"},
        {"id": "disk2", "size": "200 GB"}
    ]
    expected_md = """```markdown
Disk ID\tSize    
--------------------
disk1  \t100 GB  
disk2  \t200 GB  
```"""
    assert disks_list_to_markdown(disks_info) == expected_md

    # Testing empty disks_info
    assert disks_list_to_markdown([]) == "```No disks found.```"

def test_status_to_markdown():
    status = "running"
    vm_id_or_name = "vm1"
    expected_md = "```\nVM vm1 is currently running.\n```"
    assert status_to_markdown(status, vm_id_or_name) == expected_md

def test_backups_list_to_markdown():
    backups_list = [
        {"volume": "vol1", "size": "50", "filename": "backup1.tar.gz"},
        {"volume": "vol2", "size": "75", "filename": "backup2.tar.gz"}
    ]
    expected_md = """```markdown
Backups:
--------------------
Volume: vol1, Size: 50 GB, Filename: backup1.tar.gz
Volume: vol2, Size: 75 GB, Filename: backup2.tar.gz
```"""
    assert backups_list_to_markdown(backups_list) == expected_md
