# logger.py

import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, log_file='cisco_simulator.log'):
        self.logger = logging.getLogger('CiscoSimulator')
        self.logger.setLevel(logging.DEBUG)

        # יצירת תיקיית לוגים אם היא לא קיימת
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # הוספת תאריך לשם הקובץ
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = f'{log_dir}/{date_str}_{log_file}'

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)