# test_integration.py

import unittest
from cli_simulator import CLISimulator

class TestIntegration(unittest.TestCase):

    def setUp(self):
        self.simulator = CLISimulator()
        self.simulator.set_device_type("router")
        self.simulator.set_language("en")

    def test_full_command_flow(self):
        # Simulate entering privileged mode
        result = self.simulator.command_parser.parse_command("enable", "router", self.simulator.commands, "user")
        self.assertIn("Router#", result)
        self.assertEqual(self.simulator.mode, "privileged")

        # Simulate configuring an interface
        result = self.simulator.command_parser.parse_command("configure terminal", "router", self.simulator.commands, "privileged")
        self.assertIn("Router(config)#", result)
        self.assertEqual(self.simulator.mode, "config")

        result = self.simulator.command_parser.parse_command("interface GigabitEthernet0/0", "router", self.simulator.commands, "config")
        self.assertIn("config-if", self.simulator.mode)

        result = self.simulator.command_parser.parse_command("ip address 192.168.1.1 255.255.255.0", "router", self.simulator.commands, "config-if")
        self.assertIn("IP address configured", result)

        # Verify the configuration
        result = self.simulator.command_parser.parse_command("show running-config", "router", self.simulator.commands, "privileged")
        self.assertIn("interface GigabitEthernet0/0", result)
        self.assertIn("ip address 192.168.1.1 255.255.255.0", result)

if __name__ == '__main__':
    unittest.main()