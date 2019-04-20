import sys
import logging
import time

from watchdog.observers import Observer
from ipfs_client import IPFSClient
from content import Content
from event_handler import EventHandler


def init_logger():
    logger = logging.getLogger(__name__)
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

    return logger


if __name__ == "__main__":
    root_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    logger = init_logger()

    ipfs_client = IPFSClient(logger)
    content = Content(logger)

    content.add_list(ipfs_client.add_dir(root_dir, recursive=True, encrypted=True))

    event_handler = EventHandler(ipfs_client, content, root_dir, logger)
    observer = Observer()
    observer.schedule(event_handler, root_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
