# command_parser.py

import re
from data_manager import DataManager
from logger import Logger

class CommandParser:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.commands = self.data_manager.load_commands()
        self.command_regex = self.create_command_regex()
        self.logger = Logger()

    def create_command_regex(self):
        patterns = []
        for command in self.commands:
            patterns.append(re.escape(command['full_command']))
        pattern = "|".join(patterns)
        return re.compile(pattern)

    def parse_command(self, line, device_type, commands, current_mode):
        self.logger.debug(f"Parsing command: {line}")
        parts = line.split()
        if not parts:
            return "פקודה ריקה. הקלד '?' לעזרה."

        base_command = parts[0].lower()
        args = parts[1:]

        matching_commands = [cmd for cmd in commands if cmd['full_command'].lower().startswith(base_command) and current_mode in cmd['modes']]

        if not matching_commands:
            self.logger.warning(f"Unknown command: {base_command}")
            return f"פקודה לא מוכרת: {base_command}"

        if len(matching_commands) > 1:
            self.logger.warning(f"Ambiguous command: {base_command}")
            return f"פקודה לא חד משמעית. אפשרויות: {', '.join([cmd['full_command'] for cmd in matching_commands])}"

        command = matching_commands[0]

        if 'min_args' in command and len(args) < command['min_args']:
            self.logger.warning(f"Not enough arguments for command: {base_command}")
            return f"מספר ארגומנטים לא מספיק. מינימום נדרש: {command['min_args']}"

        if 'max_args' in command and len(args) > command['max_args']:
            self.logger.warning(f"Too many arguments for command: {base_command}")
            return f"יותר מדי ארגומנטים. מקסימום מותר: {command['max_args']}"

        return self.execute_command(command, device_type, args)

    def execute_command(self, command, device_type, args):
        self.logger.info(f"Executing command: {command['action']} with args: {args}")
        action = command['action']

        if action == 'enter_privileged':
            return self.enter_privileged_mode(device_type)
        elif action == 'enter_config':
            return self.enter_config_mode(device_type)
        elif action == 'show_running_config':
            return self.show_running_config()
        elif action == 'configure_interface':
            return self.configure_interface(args)
        elif action == 'set_ip_address':
            return self.set_ip_address(args)
        elif action == 'show_interfaces':
            return self.show_interfaces()
        else:
            self.logger.warning(f"Action not implemented: {action}")
            return f"פעולה {action} לא מיושמת עדיין."

    def enter_privileged_mode(self, device_type):
        self.logger.info(f"Entering privileged mode for {device_type}")
        return f"{device_type.capitalize()}#"

    def enter_config_mode(self, device_type):
        self.logger.info(f"Entering config mode for {device_type}")
        return f"{device_type.capitalize()}(config)#"

    def show_running_config(self):
        self.logger.info("Displaying running configuration")
        config = self.data_manager.get_device_state()
        output = f"Current configuration:\n"
        output += f"hostname {config['hostname']}\n"
        for interface, details in config['interfaces'].items():
            output += f"interface {interface}\n"
            for key, value in details.items():
                output += f" {key} {value}\n"
        return output

    def configure_interface(self, args):
        if len(args) < 1:
            self.logger.warning("Not enough arguments for configure_interface")
            return "שגיאה: נדרש שם ממשק."
        interface_name = args[0]
        self.data_manager.add_interface(interface_name, {})
        self.logger.info(f"Configured interface: {interface_name}")
        return f"נכנס למצב קונפיגורציית ממשק {interface_name}"

    def set_ip_address(self, args):
        if len(args) < 3:
            self.logger.warning("Not enough arguments for set_ip_address")
            return "שגיאה: נדרשת כתובת IP ומסיכת רשת."
        interface_name = args[0]
        ip_address = args[1]
        subnet_mask = args[2]
        self.data_manager.update_interface(interface_name, "ip_address", ip_address)
        self.data_manager.update_interface(interface_name, "subnet_mask", subnet_mask)
        self.logger.info(f"Set IP address for interface {interface_name}: {ip_address}/{subnet_mask}")
        return f"הוגדרה כתובת IP {ip_address} עם מסיכת רשת {subnet_mask} לממשק {interface_name}"

    def show_interfaces(self):
        self.logger.info("Displaying interfaces information")
        interfaces = self.data_manager.get_device_state('interfaces')
        output = "Interface Status:\n"
        for name, details in interfaces.items():
            output += f"{name}: {details.get('status', 'unknown')}, "
            output += f"IP address: {details.get('ip_address', 'not set')}/"
            output += f"{details.get('subnet_mask', 'not set')}\n"
        return output

    def complete_command(self, text, command_prefix):
        return [cmd['full_command'] for cmd in self.commands 
                if cmd['full_command'].startswith(command_prefix) and cmd['full_command'].startswith(text)]