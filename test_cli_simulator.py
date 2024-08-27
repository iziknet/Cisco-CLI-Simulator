# test_cli_simulator.py

import unittest
from unittest.mock import Mock, patch
from cli_simulator import CLISimulator
from data_manager import DataManager
from command_parser import CommandParser

class TestCLISimulator(unittest.TestCase):

    def setUp(self):
        self.simulator = CLISimulator()
        self.simulator.data_manager = Mock(spec=DataManager)
        self.simulator.command_parser = Mock(spec=CommandParser)

    def test_set_device_type(self):
        self.simulator.set_device_type("router")
        self.assertEqual(self.simulator.device_type, "router")
        self.simulator.data_manager.load_device_state.assert_called_once()

    def test_set_language(self):
        self.simulator.set_language("he")
        self.assertEqual(self.simulator.language, "he")

    def test_update_prompt(self):
        self.simulator.hostname = "TestRouter"
        self.simulator.mode = "privileged"
        self.simulator.update_prompt()
        self.assertEqual(self.simulator.prompt, "TestRouter# ")

    def test_exit_current_mode_from_user(self):
        self.simulator.mode = "user"
        self.simulator.exit_current_mode()
        self.assertFalse(self.simulator.running)

    def test_exit_current_mode_from_privileged(self):
        self.simulator.mode = "privileged"
        self.simulator.exit_current_mode()
        self.assertEqual(self.simulator.mode, "user")

    @patch('builtins.print')
    def test_print_help(self, mock_print):
        self.simulator.commands = [
            {"full_command": "show", "description_en": "Show commands", "modes": ["user"]},
            {"full_command": "configure", "description_en": "Configure", "modes": ["privileged"]}
        ]
        self.simulator.mode = "user"
        self.simulator.language = "en"
        self.simulator.print_help()
        mock_print.assert_called_with("show: Show commands")

class TestCommandParser(unittest.TestCase):

    def setUp(self):
        self.data_manager = Mock(spec=DataManager)
        self.parser = CommandParser(self.data_manager)

    def test_parse_command_valid(self):
        self.parser.commands = [
            {"full_command": "show interfaces", "action": "show_interfaces", "modes": ["privileged"]}
        ]
        result = self.parser.parse_command("show interfaces", "router", self.parser.commands, "privileged")
        self.assertIsNotNone(result)

    def test_parse_command_invalid(self):
        result = self.parser.parse_command("invalid command", "router", self.parser.commands, "user")
        self.assertIn("פקודה לא מוכרת", result)

class TestDataManager(unittest.TestCase):

    @patch('sqlite3.connect')
    def setUp(self, mock_connect):
        self.data_manager = DataManager(':memory:')
        self.data_manager.cursor = Mock()
        self.data_manager.conn = Mock()

    def test_update_hostname(self):
        self.data_manager.update_hostname("NewHostname")
        self.data_manager.cursor.execute.assert_called_with(
            "INSERT OR REPLACE INTO device_state (key, value) VALUES (?, ?)",
            ("hostname", '"NewHostname"')
        )

    def test_add_interface(self):
        self.data_manager.get_device_state = Mock(return_value={})
        self.data_manager.add_interface("GigabitEthernet0/0", {"ip": "192.168.1.1"})
        self.data_manager.cursor.execute.assert_called_with(
            "INSERT OR REPLACE INTO device_state (key, value) VALUES (?, ?)",
            ("interfaces", '{"GigabitEthernet0/0": {"ip": "192.168.1.1"}}')
        )

if __name__ == '__main__':
    unittest.main()