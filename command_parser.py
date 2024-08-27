# command_parser.py

import re
from data_manager import DataManager
from logger import Logger
import ipaddress

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
            self.logger.warning(f"Action not implemented: {action}")
            return f"פעולה {action} לא מיושמת עדיין."

    # Existing methods...

    def enter_privileged_mode(self, device_type, args):
        self.logger.info(f"Entering privileged mode for {device_type}")
        return f"Entering privileged mode\n{device_type.capitalize()}#"

    def exit_mode(self, device_type, args):
        self.logger.info(f"Exiting current mode for {device_type}")
        return "Exiting current mode"

    def enter_config_mode(self, device_type, args):
        self.logger.info(f"Entering config mode for {device_type}")
        return f"Entering configuration mode\n{device_type.capitalize()}(config)#"

    def show_running_config(self, device_type, args):
        self.logger.info("Displaying running configuration")
        config = self.data_manager.get_device_state("running_config")
        return f"Current running configuration:\n{config}"

    def show_startup_config(self, device_type, args):
        self.logger.info("Displaying startup configuration")
        config = self.data_manager.get_device_state("startup_config")
        return f"Startup configuration:\n{config}"

    def copy_running_to_startup(self, device_type, args):
        self.logger.info("Copying running configuration to startup configuration")
        self.data_manager.save_running_config()
        return "Running configuration copied to startup configuration"

    def show_interfaces(self, device_type, args):
        self.logger.info("Displaying interface information")
        interfaces = self.data_manager.get_device_state("interfaces")
        output = "Interface Status:\n"
        for name, details in interfaces.items():
            output += f"{name}: {details.get('status', 'unknown')}, "
            output += f"IP address: {details.get('ip_address', 'not set')}/"
            output += f"{details.get('subnet_mask', 'not set')}\n"
        return output

    def configure_interface(self, device_type, args):
        if len(args) < 1:
            return "Error: Interface name required."
        interface_name = args[0]
        self.data_manager.add_interface(interface_name, {})
        return f"Configuring interface {interface_name}"

    def set_ip_address(self, device_type, args):
        if len(args) < 3:
            return "Error: Interface name, IP address, and subnet mask required."
        interface_name, ip_address, subnet_mask = args[:3]
        try:
            ipaddress.ip_address(ip_address)
            ipaddress.ip_address(subnet_mask)
        except ValueError:
            return "Error: Invalid IP address or subnet mask."
        self.data_manager.update_interface(interface_name, "ip_address", ip_address)
        self.data_manager.update_interface(interface_name, "subnet_mask", subnet_mask)
        return f"IP address {ip_address}/{subnet_mask} set on interface {interface_name}"

    def show_ip_interface_brief(self, device_type, args):
        interfaces = self.data_manager.get_device_state("interfaces")
        output = "Interface\tIP-Address\tStatus\n"
        for name, details in interfaces.items():
            output += f"{name}\t{details.get('ip_address', 'unassigned')}\t{details.get('status', 'unknown')}\n"
        return output

    def show_version(self, device_type, args):
        return "Cisco IOS Software Simulator, Version 1.0"

    def set_hostname(self, device_type, args):
        if len(args) < 1:
            return "Error: Hostname required."
        hostname = args[0]
        self.data_manager.update_hostname(hostname)
        return f"Hostname set to {hostname}"

    def show_vlan(self, device_type, args):
        vlans = self.data_manager.get_device_state("vlans")
        output = "VLAN\tName\tStatus\tPorts\n"
        for vlan_id, details in vlans.items():
            output += f"{vlan_id}\t{details['name']}\tactive\t{', '.join(details['interfaces'])}\n"
        return output

    def create_vlan(self, device_type, args):
        if len(args) < 2:
            return "Error: VLAN ID and name required."
        vlan_id, name = args[:2]
        self.data_manager.add_vlan(vlan_id, name)
        return f"VLAN {vlan_id} created with name {name}"

    def configure_access_list(self, device_type, args):
        if len(args) < 3:
            return "Error: ACL ID, action (permit/deny), and IP address required."
        acl_id, action, ip = args[:3]
        rule = f"{action} {ip}"
        self.data_manager.add_access_list(acl_id, rule)
        return f"Access list {acl_id} updated: {rule}"

    def show_access_lists(self, device_type, args):
        acls = self.data_manager.get_device_state("access_lists")
        output = "Access Lists:\n"
        for acl_id, rules in acls.items():
            output += f"Access list {acl_id}:\n"
            for rule in rules:
                output += f"  {rule}\n"
        return output

    def configure_dhcp_pool(self, device_type, args):
        if len(args) < 2:
            return "Error: Pool name and network required."
        pool_name, network = args[:2]
        config = {"network": network}
        self.data_manager.add_dhcp_pool(pool_name, config)
        return f"DHCP pool {pool_name} configured for network {network}"

    def show_dhcp_bindings(self, device_type, args):
        # This would typically show actual DHCP leases, but for simulation we'll just show the pools
        dhcp_pools = self.data_manager.get_device_state("dhcp_pools")
        output = "DHCP Pools:\n"
        for pool_name, config in dhcp_pools.items():
            output += f"Pool {pool_name}: Network {config['network']}\n"
        return output

    def configure_static_route(self, device_type, args):
        if len(args) < 3:
            return "Error: Destination network, subnet mask, and next hop required."
        destination, mask, next_hop = args[:3]
        self.data_manager.add_route(f"{destination}/{mask}", next_hop)
        return f"Static route added: {destination}/{mask} via {next_hop}"

    def show_ip_route(self, device_type, args):
        routes = self.data_manager.get_device_state("routing_table")
        output = "Routing Table:\n"
        for route in routes:
            output += f"{route['destination']} via {route['next_hop']} [distance/metric] {route['distance']}/0\n"
        return output

    def configure_ospf(self, device_type, args):
        if len(args) < 2:
            return "Error: OSPF process ID and network required."
        process_id, network = args[:2]
        ospf_config = self.data_manager.get_device_state("ospf_config") or {}
        if process_id not in ospf_config:
            ospf_config[process_id] = []
        ospf_config[process_id].append(network)
        self.data_manager.update_device_state("ospf_config", ospf_config)
        return f"OSPF process {process_id} configured for network {network}"

    def show_ip_ospf(self, device_type, args):
        ospf_config = self.data_manager.get_device_state("ospf_config") or {}
        output = "OSPF Configuration:\n"
        for process_id, networks in ospf_config.items():
            output += f"OSPF process {process_id}:\n"
            for network in networks:
                output += f"  Network: {network}\n"
        return output

    def configure_eigrp(self, device_type, args):
        if len(args) < 2:
            return "Error: EIGRP AS number and network required."
        as_number, network = args[:2]
        eigrp_config = self.data_manager.get_device_state("eigrp_config") or {}
        if as_number not in eigrp_config:
            eigrp_config[as_number] = []
        eigrp_config[as_number].append(network)
        self.data_manager.update_device_state("eigrp_config", eigrp_config)
        return f"EIGRP AS {as_number} configured for network {network}"

    def show_ip_eigrp(self, device_type, args):
        eigrp_config = self.data_manager.get_device_state("eigrp_config") or {}
        output = "EIGRP Configuration:\n"
        for as_number, networks in eigrp_config.items():
            output += f"EIGRP AS {as_number}:\n"
            for network in networks:
                output += f"  Network: {network}\n"
        return output

    def complete_command(self, text, command_prefix, current_mode):
        return [cmd['full_command'] for cmd in self.commands 
                if cmd['full_command'].startswith(command_prefix) and 
                cmd['full_command'].startswith(text) and
                current_mode in cmd['modes']]
