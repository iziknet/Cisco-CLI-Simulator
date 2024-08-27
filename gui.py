import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QWidget
from cli_simulator import CLISimulator

class CLISimulatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cli_simulator = CLISimulator()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Cisco CLI Simulator')
        self.setGeometry(100, 100, 800, 600)

        # יצירת ווידג'טים
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)

        self.input_line = QLineEdit(self)
        self.input_line.returnPressed.connect(self.process_command)

        # סידור הווידג'טים
        layout = QVBoxLayout()
        layout.addWidget(self.output_area)
        layout.addWidget(self.input_line)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # אתחול הסימולטור
        self.output_area.append("ברוכים הבאים לסימולטור CLI של סיסקו!")
        self.output_area.append("אנא בחר סוג מכשיר (router/switch):")

        self.state = "choose_device"

    def process_command(self):
        command = self.input_line.text()
        self.input_line.clear()

        if self.state == "choose_device":
            if command.lower() in ["router", "switch"]:
                self.cli_simulator.set_device_type(command.lower())
                self.output_area.append(f"נבחר מכשיר: {command}")
                self.output_area.append("אנא בחר שפת ממשק (he/en):")
                self.state = "choose_language"
            else:
                self.output_area.append("בחירה לא חוקית. אנא בחר router או switch.")
        elif self.state == "choose_language":
            if command.lower() in ["he", "en"]:
                self.cli_simulator.set_language(command.lower())
                self.output_area.append(f"נבחרה שפה: {command}")
                self.output_area.append(self.cli_simulator.prompt)
                self.state = "simulator"
            else:
                self.output_area.append("בחירה לא חוקית. אנא בחר he או en.")
        elif self.state == "simulator":
            result = self.cli_simulator.default(command)
            self.output_area.append(f"{self.cli_simulator.prompt}{command}")
            self.output_area.append(result)
            self.output_area.append(self.cli_simulator.prompt)

def main():
    app = QApplication(sys.argv)
    gui = CLISimulatorGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
