# data_manager.py

import sqlite3
import json
from datetime import datetime

class DataManager:
    def __init__(self, db_name='cisco_simulator.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.commands = self.load_commands()
        self.init_device_state()

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY,
            command_data TEXT
        )''')
        self.conn.commit()

    def init_device_state(self):
        default_state = {
            "hostname": "Router",
            "interfaces": {},
            "vlans": {},
            "routing_table": [],
            "access_lists": {},
            "dhcp_pools": {},
            "ntp_config": {},
            "snmp_config": {},
            "users": [],
            "enable_password": "",
            "startup_config": "",
            "running_config": "",
        }
        for key, value in default_state.items():
            if self.get_device_state(key) is None:
                self.update_device_state(key, value)

    def load_commands(self):
        self.cursor.execute("SELECT command_data FROM commands")
        result = self.cursor.fetchone()
        if result:
            return json.loads(result[0])
        else:
            return self.load_commands_from_json()

    def load_commands_from_json(self):
        try:
            with open('commands.json', 'r', encoding='utf-8') as f:
                commands = json.load(f)['commands']
            self.save_commands(commands)
            return commands
        except FileNotFoundError:
            print("Error: commands.json file not found.")
            return []
        except json.JSONDecodeError:
            print("Error: Invalid JSON in commands.json file.")
            return []

    def save_commands(self, commands):
        command_json = json.dumps(commands)
        self.cursor.execute("DELETE FROM commands")
        self.cursor.execute("INSERT INTO commands (command_data) VALUES (?)", (command_json,))
        self.conn.commit()

    def load_device_state(self):
        self.cursor.execute("SELECT key, value FROM device_state")
        rows = self.cursor.fetchall()
        return {key: json.loads(value) for key, value in rows}

    def save_device_state(self, state):
        for key, value in state.items():
            json_value = json.dumps(value)
            self.cursor.execute("INSERT OR REPLACE INTO device_state (key, value) VALUES (?, ?)",
                                (key, json_value))
        self.conn.commit()
        print("Device state saved successfully.")

    def update_device_state(self, key, value):
        json_value = json.dumps(value)
        self.cursor.execute("INSERT OR REPLACE INTO device_state (key, value) VALUES (?, ?)",
                            (key, json_value))
        self.conn.commit()

    def get_device_state(self, key):
        self.cursor.execute("SELECT value FROM device_state WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None

    # Existing methods

    def update_hostname(self, hostname):
        self.update_device_state("hostname", hostname)

    def add_interface(self, name, config):
        interfaces = self.get_device_state("interfaces") or {}
        interfaces[name] = config
        self.update_device_state("interfaces", interfaces)

    def update_interface(self, name, key, value):
        interfaces = self.get_device_state("interfaces") or {}
        if name in interfaces:
            interfaces[name][key] = value
            self.update_device_state("interfaces", interfaces)

    def remove_interface(self, name):
        interfaces = self.get_device_state("interfaces") or {}
        interfaces.pop(name, None)
        self.update_device_state("interfaces", interfaces)

    # New methods to support additional commands

    def add_vlan(self, vlan_id, name):
        vlans = self.get_device_state("vlans") or {}
        vlans[vlan_id] = {"name": name, "interfaces": []}
        self.update_device_state("vlans", vlans)

    def remove_vlan(self, vlan_id):
        vlans = self.get_device_state("vlans") or {}
        vlans.pop(str(vlan_id), None)
        self.update_device_state("vlans", vlans)

    def add_route(self, destination, next_hop, distance=1):
        routing_table = self.get_device_state("routing_table") or []
        routing_table.append({
            "destination": destination,
            "next_hop": next_hop,
            "distance": distance,
            "time": datetime.now().isoformat()
        })
        self.update_device_state("routing_table", routing_table)

    def remove_route(self, destination):
        routing_table = self.get_device_state("routing_table") or []
        routing_table = [route for route in routing_table if route["destination"] != destination]
        self.update_device_state("routing_table", routing_table)

    def add_access_list(self, acl_id, rule):
        access_lists = self.get_device_state("access_lists") or {}
        if acl_id not in access_lists:
            access_lists[acl_id] = []
        access_lists[acl_id].append(rule)
        self.update_device_state("access_lists", access_lists)

    def remove_access_list(self, acl_id):
        access_lists = self.get_device_state("access_lists") or {}
        access_lists.pop(acl_id, None)
        self.update_device_state("access_lists", access_lists)

    def add_dhcp_pool(self, pool_name, config):
        dhcp_pools = self.get_device_state("dhcp_pools") or {}
        dhcp_pools[pool_name] = config
        self.update_device_state("dhcp_pools", dhcp_pools)

    def remove_dhcp_pool(self, pool_name):
        dhcp_pools = self.get_device_state("dhcp_pools") or {}
        dhcp_pools.pop(pool_name, None)
        self.update_device_state("dhcp_pools", dhcp_pools)

    def update_ntp_config(self, config):
        self.update_device_state("ntp_config", config)

    def update_snmp_config(self, config):
        self.update_device_state("snmp_config", config)

    def add_user(self, username, password, privilege):
        users = self.get_device_state("users") or []
        users.append({"username": username, "password": password, "privilege": privilege})
        self.update_device_state("users", users)

    def remove_user(self, username):
        users = self.get_device_state("users") or []
        users = [user for user in users if user["username"] != username]
        self.update_device_state("users", users)

    def set_enable_password(self, password):
        self.update_device_state("enable_password", password)

    def save_running_config(self):
        running_config = self.get_device_state("running_config")
        self.update_device_state("startup_config", running_config)

    def __del__(self):
        self.conn.close()
