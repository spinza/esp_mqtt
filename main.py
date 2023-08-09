#!/usr/bin/env python
import logging
from config_defaults import *
from config import *

# create logger
logger = logging.getLogger("esp_mqtt")
logger.setLevel(LOGGING_LEVEL_CONSOLE)

# create formatter and add it to the handlers
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# create file handler which logs even debug messages
if LOGGING_FILE != None:
    fh = logging.FileHandler(LOGGING_FILE)
    fh.setLevel(LOGGING_LEVEL_FILE)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(LOGGING_LEVEL_CONSOLE)
ch.setFormatter(formatter)
logger.addHandler(ch)

import esp

esp = esp.ESP()

esp.main_loop()
