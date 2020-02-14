import logging
import os
import time
import sys

################################################################################
# Modify this constant to change the name of the directory the logs will be
# stored in
LOG_DIR = 'Logs'

# Modify this constant to change the name of the log file
LOG_FILE_NAME = 'game.log'

# Modifiy the constant below to set the logging level the levels are
# DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGGING_LEVEL = logging.DEBUG
################################################################################


# DON'T MESS WITH THIS
log_path = os.path.join(LOG_DIR, LOG_FILE_NAME)

def logger_init():
    """
    Sets the logger up to log to a file and to stdout.
    Calls functions to manage old log files and setup directories if needed
    """
    log_check()
    logging.basicConfig(
        format='%(asctime)s, %(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=LOGGING_LEVEL,
        handlers=[
          logging.FileHandler(log_path),
          logging.StreamHandler(sys.stdout)
        ]
    )


def log_check():
    """
    Does checks on the state of logging infastructure. Added Log directory if 
    needed and renames old log file if needed
    """  
    if not os.path.exists(LOG_DIR):
      os.mkdir(LOG_DIR)
    if os.path.exists(log_path):
      archive_old_log()


def archive_old_log():
    """
    Archives previous log file to make room for new log file. Old log file gets
    renamed to the time is was last modified plus the old filename
    """
    file_stats = os.stat(log_path)
    ctime = file_stats.st_mtime
    formatted_time = time.strftime('%m-%d-%y_%H-%M-%S', time.localtime(ctime))
    archive_file_string = '{}_game.log'.format(formatted_time)
    os.rename(os.path.join(LOG_DIR, LOG_FILE_NAME),
              os.path.join(LOG_DIR, archive_file_string))
