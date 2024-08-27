# cli_simulator.py

import cmd
import command_parser
import data_manager
import difflib
from logger import Logger

class CLISimulator(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.device_type = None
        self.language = None
        self.prompt = ""
        self.intro = "ברוכים הבאים לסימולטור CLI של סיסקו!\n"
        self.data_manager = data_manager.DataManager()
        self.command_parser = command_parser.CommandParser(self.data_manager)
        self.commands = self.data_manager.load_commands()
        self.history = []
        self.running = True
        self.mode = "user"
        self.hostname = "Router"
        self.logger = Logger()
        self.logger.info("CLI Simulator initialized")

    def set_device_type(self, device_type):
        self.device_type = device_type
        self.data_manager.load_device_state()
        self.hostname = self.data_manager.get_device_state("hostname") or "Router"
        self.update_prompt()
        self.logger.info(f"Device type set to {device_type}")

    def set_language(self, language):
        self.language = language
        self.logger.info(f"Language set to {language}")

    def start(self):
        self.logger.info("Starting CLI Simulator")
        print(self.intro)
        self.cmdloop()

    def postcmd(self, stop, line):
        self.history.append(line)
        return stop

    def precmd(self, line):
        if line == "":
            return line
        if line == "?":
            self.print_help()
            return ""

        if line.lower() in ['quit', 'exit', 'bye']:
            return "exit"
        if line.lower() in ['help', 'h']:
            return "?"

        return line

    def print_help(self):
        self.logger.debug("Displaying help")
        print("פקודות זמינות:")
        for command in self.commands:
            if self.mode in command['modes']:
                print(f"{command['full_command']}: {command['description_' + self.language]}")

    def do_exit(self, args):
        self.logger.info("Exiting CLI Simulator")
        print("שומר את מצב המכשיר...")
        self.data_manager.save_device_state()
        print("ביי!")
        return True

    def default(self, line):
        self.logger.debug(f"Executing command: {line}")
        result = self.command_parser.parse_command(line, self.device_type, self.mode)
        if result:
            print(result)
            # בדוק אם התוצאה מכילה שינוי במצב
            if "Entering" in result or "Exiting" in result:
                self.update_mode(result)
        else:
            self.logger.warning(f"Unknown command: {line}")
            print(f"פקודה לא מוכרת: {line}")
            suggestions = self.suggest_correction(line)
            if suggestions:
                print("האם התכוונת לאחת מהפקודות הבאות?")
                for suggestion in suggestions:
                    print(f"- {suggestion}")
            else:
                print("לא נמצאו הצעות לתיקון. הקלד '?' לעזרה.")

    def update_mode(self, result):
        if "Entering privileged mode" in result:
            self.mode = "privileged"
        elif "Entering configuration mode" in result:
            self.mode = "config"
        elif "Entering interface configuration mode" in result:
            self.mode = "interface"
        elif "Exiting current mode" in result:
            if self.mode == "interface":
                self.mode = "config"
            elif self.mode == "config":
                self.mode = "privileged"
            elif self.mode == "privileged":
                self.mode = "user"
        self.update_prompt()

    def emptyline(self):
        pass

    def completedefault(self, text, line, begidx, endidx):
        return self.complete_command(text, line, begidx, endidx)

    def complete_command(self, text, line, begidx, endidx):
        return self.command_parser.complete_command(text, line[:begidx].strip(), self.mode)

    def suggest_correction(self, command):
        all_commands = [cmd['full_command'] for cmd in self.commands if self.mode in cmd['modes']]
        suggestions = difflib.get_close_matches(command, all_commands, n=3, cutoff=0.6)
        return suggestions

    def update_prompt(self):
        if self.mode == "user":
            self.prompt = f"{self.hostname}> "
        elif self.mode == "privileged":
            self.prompt = f"{self.hostname}# "
        elif self.mode == "config":
            self.prompt = f"{self.hostname}(config)# "
        elif self.mode.startswith("config-"):
            self.prompt = f"{self.hostname}({self.mode})# "
        elif self.mode == "interface":
            self.prompt = f"{self.hostname}(config-if)# "
        elif self.mode == "vlan":
            self.prompt = f"{self.hostname}(config-vlan)# "
        elif self.mode == "router":
            self.prompt = f"{self.hostname}(config-router)# "
        # הוסף כאן עוד מצבים לפי הצורך

    def do_hostname(self, arg):
        if self.mode == "config":
            self.hostname = arg
            self.data_manager.update_hostname(arg)
            self.update_prompt()
            self.logger.info(f"Hostname set to {arg}")
            print(f"Hostname set to {arg}")
        else:
            print("Command available only in configuration mode")

    def do_show(self, arg):
        result = self.command_parser.parse_command(f"show {arg}", self.device_type, self.mode)
        print(result)

if __name__ == "__main__":
    simulator = CLISimulator()
    simulator.start()
