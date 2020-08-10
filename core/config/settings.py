import sys
import os
import logging.config

ROOT_DIR = os.path.abspath(os.path.dirname(sys.modules['__main__'].__file__))
BASE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT_DIR, "data")
TMP_PATH = os.path.join(ROOT_DIR, "tmp")
LOG_PATH = os.path.join(ROOT_DIR, "logs")

logging.config.fileConfig(os.path.abspath(os.path.join(CURRENT_PATH, 'logging.ini')))
logger = logging.getLogger("pds")
