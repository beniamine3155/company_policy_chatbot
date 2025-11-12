import sys
from utils.logger import logger

class CustomException(Exception):
    def __init__(self, error_message, error_detail=None):
        super().__init__(error_message)
        self.error_message = error_message
        self.error_detail = error_detail
        logger.error(f"CustomException: {error_message} - Detail: {error_detail}")
    
    def __str__(self):
        return self.error_message

def error_message_detail(error, error_detail):
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    error_message = f"Error occurred in file: {file_name} at line: {line_number} - {str(error)}"
    return error_message