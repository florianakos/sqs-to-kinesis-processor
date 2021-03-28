import sys
import os
import logging

def init_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(level=os.environ.get("LOG_LEVEL", "INFO"))
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    sh.flush = sys.stdout.flush
    logger.addHandler(sh)
    return logger
