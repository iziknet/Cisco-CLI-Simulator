# test_cli_simulator.py

import unittest
from unittest.mock import Mock, patch
from cli_simulator import CLISimulator
from data_manager import DataManager
from command_parser import CommandParser, CommandError

class TestCLISimulator(unittest.TestCase):

    def setUp(self):
        self.simulator = CLISimulator()
        self.simulator.data_manager = Mock(spec=DataManager)
        self.simulator.command_parser = Mock(spec=CommandParser)

    def test_set_device_type_valid(self):
        self.simulator.set_device_type("router")
        self.assertEqual(self.simulator.device_type, "router")
        self.simulator.data_manager.load_device_state.assert_called_once()

    def test_set_device_type_invalid(self):
        with self.assertRaises(ValueError):
            self.simulator.set_device_type("invalid_device")

    def test_set_language_valid(self):
        self.simulator.set_language("he")
        self.assertEqual(self.simulator.language, "he")

    def test_set_language_invalid(self):
        with self.assertRaises(ValueError):
            self.simulator.set_language("invalid_language")

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

    def test_suggest_correction(self):
        self.simulator.commands = [
            {"full_command": "show interfaces", "modes": ["privileged"]},
            {"full_command": "show ip route", "modes": ["privileged"]}
        ]
        self.simulator.mode = "privileged"
        suggestions = self.simulator.suggest_correction("show int")
        self.assertIn("show interfaces", suggestions)

    @patch('builtins.print')
    def test_do_exit(self, mock_print):
        result = self.simulator.do_exit("")
        self.assertTrue(result)
        self.simulator.data_manager.save_device_state.assert_called_once()

    def test_default_known_command(self):
        self.simulator.command_parser.parse_command.return_value = "Command executed"
        self.simulator.default("show interfaces")
        self.simulator.command_parser.parse_command.assert_called_with("show interfaces", self.simulator.device_type, self.simulator.mode)

    def test_default_unknown_command(self):
        self.simulator.command_parser.parse_command.side_effect = CommandError("Unknown command")
        with patch('builtins.print') as mock_print:
            self.simulator.default("unknown_command")
            mock_print.assert_called_with("פקודה לא מוכרת: unknown_command")

class TestCommandParser(unittest.TestCase):

    def setUp(self):
        self.data_manager = Mock(spec=DataManager)
        self.parser = CommandParser(self.data_manager)

    def test_parse_command_valid(self):
        self.parser.commands = [
            {"full_command": "show interfaces", "action": "show_interfaces", "modes": ["privileged"]}
        ]
        result = self.parser.parse_command("show interfaces", "router", "privileged")
        self.assertIsNotNone(result)

    def test_parse_command_invalid(self):
        with self.assertRaises(CommandError):
            self.parser.parse_command("invalid command", "router", "user")

    def test_set_ip_address_valid(self):
        args = ["GigabitEthernet0/0", "192.168.1.1", "255.255.255.0"]
        result = self.parser.set_ip_address("router", args)
        self.assertIn("IP address 192.168.1.1/255.255.255.0 set on interface GigabitEthernet0/0", result)

    def test_set_ip_address_invalid(self):
        args = ["GigabitEthernet0/0", "invalid_ip", "invalid_mask"]
        with self.assertRaises(CommandError):
            self.parser.set_ip_address("router", args)

    def test_configure_static_route_valid(self):
        args = ["192.168.2.0", "255.255.255.0", "10.0.0.1"]
        result = self.parser.configure_static_route("router", args)
        self.assertIn("Static route added: 192.168.2.0/255.255.255.0 via 10.0.0.1", result)

    def test_configure_static_route_invalid(self):
        args = ["invalid_network", "invalid_mask", "invalid_next_hop"]
        with self.assertRaises(CommandError):
            self.parser.configure_static_route("router", args)

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

    def test_add_route(self):
        self.data_manager.get_device_state = Mock(return_value=[])
        self.data_manager.add_route("192.168.2.0/24", "10.0.0.1")
        self.data_manager.cursor.execute.assert_called()  # We can't check the exact arguments due to the timestamp

    def test_add_vlan(self):
        self.data_manager.get_device_state = Mock(return_value={})
        self.data_manager.add_vlan("10", "Sales")
        self.data_manager.cursor.execute.assert_called_with(
            "INSERT OR REPLACE INTO device_state (key, value) VALUES (?, ?)",
            ("vlans", '{"10": {"name": "Sales", "interfaces": []}}')
        )

if __name__ == '__main__':
    unittest.main()
