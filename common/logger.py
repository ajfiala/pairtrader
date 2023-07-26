import logging
import logging.config
from os import path

log_file_path = path.join(path.dirname(path.abspath(__file__)), '..', 'config', 'logging.conf')
logging.config.fileConfig(log_file_path)

# create logger
log = logging.getLogger('pairtrade')

def get_logger(name):
    return logging.getLogger(name)