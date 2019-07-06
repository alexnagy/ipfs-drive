import logging
import multiaddr.codecs.idna
import multiaddr.codecs.uint16be
import sys

# from controller import Controller
from gui.gui import IPFSDrive


def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create a file handler
    handler = logging.FileHandler("client.log")
    handler.setLevel(logging.DEBUG)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)


if __name__ == "__main__":
    init_logger()
    IPFSDrive().run()
    sys.exit(0)
