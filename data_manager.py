# data_manager.py

import sqlite3
import json

class DataManager:
    """
    מנהל את הנתונים של סימולטור ה-CLI של סיסקו.
    אחראי על שמירה וטעינה של מצב המכשיר ופקודות מ/אל מסד נתונים SQLite.
    """

    def __init__(self, db_name='cisco_simulator.db'):
        """
        אתחול מנהל הנתונים.

        :param db_name: שם קובץ מסד הנתונים SQLite
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.commands = self.load_commands()

    def create_tables(self):
        """יוצר את הטבלאות הנדרשות במסד הנתונים אם הן לא קיימות."""
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
        """
        טוען את רשימת הפקודות ממסד הנתונים.

        :return: רשימת הפקודות
        """
        self.cursor.execute("SELECT command_data FROM commands")
        result = self.cursor.fetchone()
        if result:
            return json.loads(result[0])
        else:
            return self.load_commands_from_json()

    def load_commands_from_json(self):
        """
        טוען פקודות מקובץ JSON חיצוני ושומר אותן במסד הנתונים.

        :return: רשימת הפקודות
        """
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
        """
        שומר את רשימת הפקודות במסד הנתונים.

        :param commands: רשימת הפקודות לשמירה
        """
        command_json = json.dumps(commands)
        self.cursor.execute("DELETE FROM commands")
        self.cursor.execute("INSERT INTO commands (command_data) VALUES (?)", (command_json,))
        self.conn.commit()

    def load_device_state(self):
        """
        טוען את מצב המכשיר ממסד הנתונים.

        :return: מילון המייצג את מצב המכשיר
        """
        self.cursor.execute("SELECT key, value FROM device_state")
        rows = self.cursor.fetchall()
        return {key: json.loads(value) for key, value in rows}

    def save_device_state(self, state):
        """
        שומר את מצב המכשיר במסד הנתונים.

        :param state: מילון המייצג את מצב המכשיר לשמירה
        """
        for key, value in state.items():
            json_value = json.dumps(value)
            self.cursor.execute("INSERT OR REPLACE INTO device_state (key, value) VALUES (?, ?)",
                                (key, json_value))
        self.conn.commit()
        print("Device state saved successfully.")

    def update_device_state(self, key, value):
        """
        מעדכן ערך ספציפי במצב המכשיר.

        :param key: המפתח לעדכון
        :param value: הערך החדש
        """
        json_value = json.dumps(value)
        self.cursor.execute("INSERT OR REPLACE INTO device_state (key, value) VALUES (?, ?)",
                            (key, json_value))
        self.conn.commit()

    def get_device_state(self, key):
        """
        מקבל ערך ספציפי ממצב המכשיר.

        :param key: המפתח לקבלת הערך שלו
        :return: הערך המבוקש, או None אם לא נמצא
        """
        self.cursor.execute("SELECT value FROM device_state WHERE key = ?", (key,))
        result = self.cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None

    def update_hostname(self, hostname):
        """
        מעדכן את שם המארח של המכשיר.

        :param hostname: שם המארח החדש
        """
        self.update_device_state("hostname", hostname)

    def add_interface(self, name, config):
        """
        מוסיף ממשק חדש למכשיר.

        :param name: שם הממשק
        :param config: תצורת הממשק
        """
        interfaces = self.get_device_state("interfaces") or {}
        interfaces[name] = config
        self.update_device_state("interfaces", interfaces)

    def update_interface(self, name, key, value):
        """
        מעדכן פרט ספציפי של ממשק.

        :param name: שם הממשק
        :param key: המפתח לעדכון
        :param value: הערך החדש
        """
        interfaces = self.get_device_state("interfaces") or {}
        if name in interfaces:
            interfaces[name][key] = value
            self.update_device_state("interfaces", interfaces)

    def remove_interface(self, name):
        """
        מסיר ממשק מהמכשיר.

        :param name: שם הממשק להסרה
        """
        interfaces = self.get_device_state("interfaces") or {}
        interfaces.pop(name, None)
        self.update_device_state("interfaces", interfaces)

    def add_route(self, destination, next_hop, metric=1):
        """
        מוסיף נתיב חדש לטבלת הניתוב.

        :param destination: היעד
        :param next_hop: הקפיצה הבאה
        :param metric: המטריקה של הנתיב (ברירת מחדל: 1)
        """
        routing_table = self.get_device_state("routing_table") or []
        routing_table.append({
            "destination": destination,
            "next_hop": next_hop,
            "metric": metric
        })
        self.update_device_state("routing_table", routing_table)

    def remove_route(self, destination):
        """
        מסיר נתיב מטבלת הניתוב.

        :param destination: היעד של הנתיב להסרה
        """
        routing_table = self.get_device_state("routing_table") or []
        routing_table = [route for route in routing_table if route["destination"] != destination]
        self.update_device_state("routing_table", routing_table)

    def __del__(self):
        """סוגר את החיבור למסד הנתונים בעת השמדת האובייקט."""
        self.conn.close()