import logging
import time
import os
import json
import subprocess
import shutil

from watchdog.observers import Observer
from ipfs_client import IPFSClient
from content import Content
from event_handler import EventHandler
from directory import Directory
from file import File
from database import Db
from sync import Sync
from encryption.aes_cipher import AESCipher


def load_cfg_data():
    cfg_data = json.load(open("client.cfg"))
    return cfg_data["rootDir"], cfg_data["workingDir"], cfg_data["sync"], cfg_data["email"], cfg_data["password"], \
           cfg_data["encryptionPassword"]


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


def add_root_dir():
    for path in os.listdir(root_dir):
        full_path = os.path.join(root_dir, path).replace(os.sep, '/')
        if os.path.getctime(full_path) >= start_time:
            continue
        if os.path.isfile(full_path):
            file = File(full_path)
            hash = ipfs_client.add_file(file)
            content.add(file.path, hash)
        elif os.path.isdir(full_path):
            content_list = ipfs_client.add_dir(Directory(full_path), recursive=True)
            content.add_list(content_list)


if __name__ == "__main__":
    root_dir, working_dir, sync, email, password, encryption_password = load_cfg_data()
    root_dir = root_dir.replace(os.sep, '/')

    ipfs_daemon = subprocess.Popen('ipfs daemon')

    time.sleep(5)

    start_time = time.time()

    logger = init_logger()

    cipher = AESCipher(encryption_password)
    ipfs_client = IPFSClient(cipher, working_dir, logger)
    db = Db(email, password)
    content = Content(root_dir, db, logger)

    if sync:
        Sync(root_dir, working_dir, db, ipfs_client, cipher, logger).sync()

    add_root_dir()

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

    shutil.rmtree(working_dir)

    ipfs_daemon.terminate()