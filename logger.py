import logging
import sys
import os
from contextlib import contextmanager
from io import StringIO

#logger for signal wire consumer
sw_logger = logging.getLogger('sw_logger')
sw_logger.setLevel(logging.DEBUG)

sw_info_handler = logging.FileHandler('./logs/sw_log.log')
sw_info_handler.setLevel(logging.INFO)

sw_err_handler = logging.FileHandler('./logs/sw_err.log')
sw_err_handler.setLevel(logging.ERROR)

sw_info_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sw_info_handler.setFormatter(sw_info_format)
sw_err_handler.setFormatter(sw_info_format)

sw_logger.addHandler(sw_info_handler)
sw_logger.addHandler(sw_err_handler)


# logging for the qa_chain function
qa_logger = logging.getLogger('qa_logger')
qa_logger.setLevel(logging.DEBUG)

qa_log_handler = logging.FileHandler('./logs/qa_log.log')
qa_log_handler.setLevel(logging.INFO)

qa_err_handler = logging.FileHandler('./logs/qa_err.log')
qa_err_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
qa_log_handler.setFormatter(formatter)
qa_err_handler.setFormatter(formatter)

qa_logger.addHandler(qa_log_handler)
qa_logger.addHandler(qa_err_handler)

socket_logger = logging.getLogger('socket_logger')
socket_logger.setLevel(logging.DEBUG)

socket_log_handler = logging.FileHandler('./logs/socket_log.log')
socket_log_handler.setLevel(logging.INFO)

socket_err_handler = logging.FileHandler('./logs/socket_err.log')
socket_err_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
socket_log_handler.setFormatter(formatter)
socket_err_handler.setFormatter(formatter)

socket_logger.addHandler(socket_log_handler)
socket_logger.addHandler(socket_err_handler)

class StreamToLogger:
    """
    Redirects writes to a stream to a logger instance.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

@contextmanager
def capture_output(logger):
    """
    Context manager to capture stdout and stderr and redirect to logger.
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)
    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr