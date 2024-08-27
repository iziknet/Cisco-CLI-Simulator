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

    def parse_command(self, line, device_type, current_mode):
        self.logger.debug(f"Parsing command: {line}")
        parts = line.split()
        if not parts:
            return "פקודה ריקה. הקלד '?' לעזרה."

        base_command = parts[0].lower()
        args = parts[1:]

        matching_commands = [cmd for cmd in self.commands if cmd['full_command'].lower().startswith(base_command) and current_mode in cmd['modes']]

        if not matching_commands:
            self.logger.warning(f"Unknown command: {base_command}")
            return f"פקודה לא מוכרת: {base_command}"

        if len(matching_commands) > 1:
            self.logger.warning(f"Ambiguous command: {base_command}")
            return f"פקודה לא חד משמעית. אפשרויות: {', '.join([cmd['full_command'] for cmd in matching_commands])}"

        command = matching_commands[0]

        return self.execute_command(command, device_type, args)

    def execute_command(self, command, device_type, args):
        self.logger.info(f"Executing command: {command['action']} with args: {args}")
        action = command['action']

        # הוסף את כל הפעולות החדשות כאן
        actions = {
            'enter_privileged': self.enter_privileged_mode,
            'exit_mode': self.exit_mode,
            'enter_config': self.enter_config_mode,
            'show_running_config': self.show_running_config,
            'show_startup_config': self.show_startup_config,
            'copy_running_to_startup': self.copy_running_to_startup,
            'copy_running_to_tftp': self.copy_running_to_tftp,
            'show_interfaces': self.show_interfaces,
            'show_ip_interface_brief': self.show_ip_interface_brief,
            'show_version': self.show_version,
            'reload_device': self.reload_device,
            'set_hostname': self.set_hostname,
            'enter_interface_config': self.enter_interface_config,
            'enable_interface': self.enable_interface,
            'disable_interface': self.disable_interface,
            'show_cdp_neighbors': self.show_cdp_neighbors,
            'show_clock': self.show_clock,
            'set_clock': self.set_clock,
            'show_users': self.show_users,
            'show_history': self.show_history,
            'set_terminal_history_size': self.set_terminal_history_size,
            'show_tech_support': self.show_tech_support,
            'show_processes': self.show_processes,
            'show_memory': self.show_memory,
            'enable_debugging': self.enable_debugging,
            'disable_debugging': self.disable_debugging,
            'show_debug_settings': self.show_debug_settings,
            'send_ping': self.send_ping,
            'perform_traceroute': self.perform_traceroute,
            # הוסף את כל הפעולות החדשות כאן...
        }

        if action in actions:
            return actions[action](device_type, args)
        else:
            self.logger.warning(f"Action not implemented: {action}")
            return f"פעולה {action} לא מיושמת עדיין."

    # יש להוסיף את כל הפונקציות החדשות כאן. להלן כמה דוגמאות:

    def enter_privileged_mode(self, device_type, args):
        self.logger.info(f"Entering privileged mode for {device_type}")
        return f"{device_type.capitalize()}#"

    def exit_mode(self, device_type, args):
        self.logger.info(f"Exiting current mode for {device_type}")
        return "Exited current mode"

    def enter_config_mode(self, device_type, args):
        self.logger.info(f"Entering config mode for {device_type}")
        return f"{device_type.capitalize()}(config)#"

    def show_running_config(self, device_type, args):
        self.logger.info("Displaying running configuration")
        config = self.data_manager.get_device_state()
        output = f"Current configuration:\n"
        output += f"hostname {config['hostname']}\n"
        for interface, details in config['interfaces'].items():
            output += f"interface {interface}\n"
            for key, value in details.items():
                output += f" {key} {value}\n"
        return output

    # הוסף את כל הפונקציות החדשות כאן...

    def complete_command(self, text, command_prefix, current_mode):
        return [cmd['full_command'] for cmd in self.commands 
                if cmd['full_command'].startswith(command_prefix) and 
                cmd['full_command'].startswith(text) and
                current_mode in cmd['modes']]
