# data_manager.py

import sqlite3
import json

class DataManager:
    def __init__(self, db_name='cisco_simulator.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.commands = self.load_commands()

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

    def __del__(self):
        self.conn.close()
