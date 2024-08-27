import cmd
import cli_simulator

def main():
    # יצירת לולאה ראשית שמקבלת קלט מהמשתמש ומעבירה אותו למעבד הפקודות
    simulator = cli_simulator.CLISimulator()

    print("ברוכים הבאים לסימולטור CLI של סיסקו!")
    print("אנא בחר סוג מכשיר:")
    print("1. נתב")
    print("2. מתג")
    device_type = input("> ")

    if device_type == "1":
        simulator.set_device_type("router")
    elif device_type == "2":
        simulator.set_device_type("switch")
    else:
        print("אנא בחר נתב או מתג.")
        return

    print("אנא בחר שפת ממשק:")
    print("1. עברית")
    print("2. אנגלית")
    language = input("> ")

    if language == "1":
        simulator.set_language("he")
    elif language == "2":
        simulator.set_language("en")
    else:
        print("אנא בחר עברית או אנגלית.")
        return

    # התחלת הסימולטור
    simulator.start()

if __name__ == "__main__":
    main()