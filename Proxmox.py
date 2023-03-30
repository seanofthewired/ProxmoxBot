from proxmoxer import ProxmoxAPI
import requests
import json
import math

game_vms = {
    "VM Name": VM ID,
    "VM Name": VM ID,
    "VM Name": VM ID,
    }

num_vms = {
    "ID":"ID",
    "ID":"ID",
    "ID":"ID",
    }

def ProxmoxToken():
    url = 'https://IP Address of Proxmox goes here:8006/api2/json/access/ticket'
    data = {'username': 'API@pve', 'password': 'Password of Proxmox Account'}
    print (data)
    response = requests.post(url, json=data, allow_redirects=True, verify=False)
    jsonResponse = response.json()
    return jsonResponse

def get_memory_ussage(vm_id):
    jsonResponse = ProxmoxToken()
    vm_id_str = str(vm_id)
    url = 'https://IP Address of Proxmox goes here:8006/api2/json/nodes/Proxmox Node Name Goes Here/qemu/' + vm_id_str + '/status/current'
   
    CSRFPreventionToken = jsonResponse["data"]["CSRFPreventionToken"]
    ticket = jsonResponse["data"]["ticket"]
    cookies = {'PVEAuthCookie': ticket}
    headers = {'CSRFPreventionToken': CSRFPreventionToken}

    data = requests.get(url, cookies=cookies, headers=headers, allow_redirects=True, verify=False)
    data = data.json()

    return data["data"]["mem"], data["data"]["maxmem"]


def get_status_all():
    messages = []
    for key, value in game_vms.items():
        messages.append(key +"\t" + str(value) +"\t" + StatusVirtualMachine(value) +"\t" + str(bytes_to_gb(get_memory_ussage(value)[0])) + "GB / " + str(bytes_to_gb(get_memory_ussage(value)[1])) + "GB")
    return "\n".join(messages)

def bytes_to_gb(bytes):
    gb = bytes / 1073741824
    return round(gb, 2)

def StatusVirtualMachine(VMid):
    print(type(VMid))
    jsonResponse = ProxmoxToken()
    VMid = str(VMid)

    num = str(num_vms[VMid])
    
    url = 'https://IP Address of Proxmox goes here:8006/api2/json/nodes/Proxmox Node Name Goes Here/qemu/' + num + '/status/current'
    CSRFPreventionToken = jsonResponse["data"]["CSRFPreventionToken"]
    ticket = jsonResponse["data"]["ticket"]
    cookies = {'PVEAuthCookie': ticket}
    headers = {'CSRFPreventionToken': CSRFPreventionToken}

    x = requests.get(url, cookies=cookies, headers=headers, allow_redirects=True, verify=False)
    x = x.json()
    status = x["data"]["qmpstatus"]
    return status

def StartVirtualMachine(VMid):
    jsonResponse = ProxmoxToken()
    VMid = str(VMid)
    num = num_vms[VMid]
    url = 'https://IP Address of Proxmox goes here:8006/api2/json/nodes/Proxmox Node Name Goes Here/qemu/' + num + '/status/start'
   
    CSRFPreventionToken = jsonResponse["data"]["CSRFPreventionToken"]
    ticket = jsonResponse["data"]["ticket"]
    cookies = {'PVEAuthCookie': ticket}
    headers = {'CSRFPreventionToken': CSRFPreventionToken}

    x = requests.post(url, cookies=cookies, headers=headers, allow_redirects=True, verify=False)

    #print(x.text)

def StopVirtualMachine(VMid):
    jsonResponse = ProxmoxToken()
    VMid = str(VMid)
    num = num_vms[VMid]
    url = 'https://IP Address of Proxmox goes here:8006/api2/json/nodes/Proxmox Node Name Goes Here/qemu/' + num + '/status/stop'
   
    CSRFPreventionToken = jsonResponse["data"]["CSRFPreventionToken"]
    ticket = jsonResponse["data"]["ticket"]
    cookies = {'PVEAuthCookie': ticket}
    headers = {'CSRFPreventionToken': CSRFPreventionToken}

    x = requests.post(url, cookies=cookies, headers=headers, allow_redirects=True, verify=False)

    #print(x.text)

def InfoVirtualMachine(VMid):
    jsonResponse = ProxmoxToken()
    VMid = str(VMid)
    url = 'https://IP Address of Proxmox goes here:8006/api2/json/nodes/Proxmox Node Name Goes Here/qemu/' + VMid + '/status/start'
   
    CSRFPreventionToken = jsonResponse["data"]["CSRFPreventionToken"]
    ticket = jsonResponse["data"]["ticket"]
    cookies = {'PVEAuthCookie': ticket}
    headers = {'CSRFPreventionToken': CSRFPreventionToken}

    x = requests.post(url, cookies=cookies, headers=headers, allow_redirects=True, verify=False)
    
    #print(x.text)
