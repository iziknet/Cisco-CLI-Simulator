# command_parser.py

import re
from data_manager import DataManager
from logger import Logger
import ipaddress

class CommandError(Exception):
    pass

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
            raise CommandError("פקודה ריקה. הקלד '?' לעזרה.")

        base_command = parts[0].lower()
        args = parts[1:]

        matching_commands = [cmd for cmd in self.commands if cmd['full_command'].lower().startswith(base_command) and current_mode in cmd['modes']]

        if not matching_commands:
            raise CommandError(f"פקודה לא מוכרת: {base_command}")

        if len(matching_commands) > 1:
            raise CommandError(f"פקודה לא חד משמעית. אפשרויות: {', '.join([cmd['full_command'] for cmd in matching_commands])}")

        command = matching_commands[0]

        return self.execute_command(command, device_type, args)

    def execute_command(self, command, device_type, args):
        self.logger.info(f"Executing command: {command['action']} with args: {args}")
        action = command['action']

        actions = {
            'enter_privileged': self.enter_privileged_mode,
            'exit_mode': self.exit_mode,
            'enter_config': self.enter_config_mode,
            'show_running_config': self.show_running_config,
            'show_startup_config': self.show_startup_config,
            'copy_running_to_startup': self.copy_running_to_startup,
            'show_interfaces': self.show_interfaces,
            'configure_interface': self.configure_interface,
            'set_ip_address': self.set_ip_address,
            'show_ip_interface_brief': self.show_ip_interface_brief,
            'show_version': self.show_version,
            'set_hostname': self.set_hostname,
            'show_vlan': self.show_vlan,
            'create_vlan': self.create_vlan,
            'configure_access_list': self.configure_access_list,
            'show_access_lists': self.show_access_lists,
            'configure_dhcp_pool': self.configure_dhcp_pool,
            'show_dhcp_bindings': self.show_dhcp_bindings,
            'configure_static_route': self.configure_static_route,
            'show_ip_route': self.show_ip_route,
            'configure_ospf': self.configure_ospf,
            'show_ip_ospf': self.show_ip_ospf,
            'configure_eigrp': self.configure_eigrp,
            'show_ip_eigrp': self.show_ip_eigrp,
        }

        if action in actions:
            return actions[action](device_type, args)
        else:
            raise CommandError(f"פעולה {action} לא מיושמת עדיין.")

    # ... (rest of the methods remain the same, but we'll update a few as examples)

    def set_ip_address(self, device_type, args):
        if len(args) < 3:
            raise CommandError("Error: Interface name, IP address, and subnet mask required.")
        interface_name, ip_address, subnet_mask = args[:3]
        try:
            ipaddress.ip_address(ip_address)
            ipaddress.ip_address(subnet_mask)
        except ValueError:
            raise CommandError("Error: Invalid IP address or subnet mask.")
        self.data_manager.update_interface(interface_name, "ip_address", ip_address)
        self.data_manager.update_interface(interface_name, "subnet_mask", subnet_mask)
        return f"IP address {ip_address}/{subnet_mask} set on interface {interface_name}"

    def configure_static_route(self, device_type, args):
        if len(args) < 3:
            raise CommandError("Error: Destination network, subnet mask, and next hop required.")
        destination, mask, next_hop = args[:3]
        try:
            ipaddress.ip_network(f"{destination}/{mask}")
            ipaddress.ip_address(next_hop)
        except ValueError:
            raise CommandError("Error: Invalid IP address, subnet mask, or next hop.")
        self.data_manager.add_route(f"{destination}/{mask}", next_hop)
        return f"Static route added: {destination}/{mask} via {next_hop}"

    # ... (other methods remain the same)

    def complete_command(self, text, command_prefix, current_mode):
        return [cmd['full_command'] for cmd in self.commands 
                if cmd['full_command'].startswith(command_prefix) and 
                cmd['full_command'].startswith(text) and
                current_mode in cmd['modes']]
