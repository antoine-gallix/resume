import sys

from loguru import logger

# print only the log message, no timestamp/level/module prefix
logger.remove()
logger.add(sys.stderr, format="{message}", level="INFO")
