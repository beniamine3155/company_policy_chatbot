import logging
import os
from datetime import datetime
from utils.config import Config

class Logger:
    def __init__(self, log_file=None):
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        self.logger = logging.getLogger("CompanyPolicyChatbot")
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        log_file = log_file or Config.LOG_FILE
        file_handler = logging.FileHandler(f"logs/{log_file}")
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Add handlers if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_logger(self):
        return self.logger


logger = Logger().get_logger()