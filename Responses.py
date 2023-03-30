import string
import Proxmox

game_vms = {
    "VM Name": "VM ID",
    "VM Name": "VM ID",
    "VM Name": "VM ID",
    "VM Name": "VM ID",
    }

def handle_response(message) -> str:
       p_message = message.lower()

       if "help" in p_message:
           return "Here are a list of commands: \n Servers - lists all servers \n Start *insert VM ID here* - will start a vm if not already running \n Stop *insert VM ID here* - will stop a vm if not already running \n Status *insert VM ID here* - will show status of a vm \n About - short description about the bot as well as how to join the servers \n 000 - for the curious \n Help or Commands - lists some commands"

       elif "commands" in p_message:
           return "Here are a list of commands: \n Servers - lists all servers \n Start *insert VM ID here* - will start a vm if not already running \n Stop *insert VM ID here* - will stop a vm if not already running \n Status *insert VM ID here* - will show status of a vm \n About - short description about the bot as well as how to join the servers \n 000 - for the curious \n Help or Commands - lists some commands"

       elif "start" in p_message:
           VMid = int(p_message.strip(string.ascii_letters))
           Proxmox.StartVirtualMachine(VMid)
           return "The VM is now running"

       elif "stop" in p_message:
           VMid = int(p_message.strip(string.ascii_letters))
           Proxmox.StopVirtualMachine(VMid)
           return "The VM is now stopped"

       elif "000" in p_message:
           return p_message+"0"
       
       elif "proxmoxbot" in p_message:
           return "Hello, I am a bot used to control game servers hosted on proxmox. Instructions to join servers can be found at https://discord.com/channels/EnterYourChannelInfoHere or by messaging YourNameHere"
       
       elif "info" in p_message:
           return "Hello, I am a bot used to control game servers hosted on proxmox. Instructions to join servers can be found at https://discord.com/channels/EnterYourChannelInfoHere or by messaging YourNameHere"

       elif "about" in p_message:
           return "Hello, I am a bot used to control game servers hosted on proxmox. Instructions to join servers can be found at https://discord.com/channels/EnterYourChannelInfoHere or by messaging YourNameHere"
       
       elif "servers" in p_message:
           return "__VM Name"+"\t"+"VM ID " +"\t" + "Status " +"\t" + "Current RAM Usage / " + "Max Allowed RAM__\n" + Proxmox.get_status_all()

       elif "status" in p_message:
           VMid = int(p_message.strip(string.ascii_letters))
           return "The VM is currently " + Proxmox.StatusVirtualMachine(VMid)

       else:
           msg = "Sorry I didnt understand that. Type help for commands"
           return 
       


