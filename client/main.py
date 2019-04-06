import sys
import time
import ipfsapi
import json
import os
import logging
from watchdog.observers import Observer
from watchdog.events import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler("client.log")
handler.setLevel(logging.DEBUG)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
consoleHandler.setLevel(logging.INFO)
logger.addHandler(consoleHandler)


dir_map = {}


def add_to_dir_map(file_tuple_list):
    global dir_map

    for name, hash in file_tuple_list:
        if name:
            dir_map[name] = hash

    logger.debug(json.dumps(dir_map, indent=4))


class IPFSApi:
    def __init__(self):
        self.conn = ipfsapi.connect('127.0.0.1', 5001)

    def add_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        res = self.conn.add(file_path)
        logger.info("Added %s to IPFS" % file_path)
        logger.debug(json.dumps(res, indent=4))
        return res['Name'], res['Hash']

    def add_dir(self, dir_path, recursive):
        if not os.path.exists(dir_path):
            raise FileNotFoundError(dir_path)

        # dir_path += '/'

        logger.debug("Adding %s to IPFS" % dir_path)

        res = self.conn.add(dir_path, recursive)

        logger.info("Added %s to IPFS" % dir_path)
        logger.debug(json.dumps(res, indent=4))

        if isinstance(res, list):
            return [(_dict_['Name'], _dict_['Hash']) for _dict_ in res]
        elif isinstance(res, dict):
            return [(res['Name'], res['Hash'])]
        else:
            raise Exception("Unhandled response instance %s!" % type(res))

    def add_link(self, root, name, ref):
        res = self.conn.object_patch_add_link(root, name, ref)
        logger.info("Added link to (%s, %s) from %s" % (name, ref, root))
        logger.debug(json.dumps(res, indent=4))
        return res["Hash"]

    def rm_link(self, root, link):
        res = self.conn.object_patch_rm_link(root, link)
        logger.info("Removed link to %s from %s" % (link, root))
        logger.debug(json.dumps(res, indent=4))

    def ls(self, hash):
        res = self.conn.ls(hash)
        logger.debug(json.dumps(res, indent=4))


class EventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # print("EVENT")
        # print(event.event_type)
        # print(event.src_path)
        # if hasattr(event, 'dest_path'):
        #     print(event.dest_path)
        # print()
        pass

    def on_created(self, event):
        src_path = event.src_path.replace(os.sep, '/')
        logger.info("CREATED %s" % src_path)
        if os.path.isdir(src_path):
            parent_dir = os.path.dirname(src_path)
            dir_to_add = os.path.basename(src_path)

            current_dir = os.getcwd()
            os.chdir(parent_dir)
            dir_content = ipfs_api.add_dir(dir_to_add, True)
            os.chdir(current_dir)

            new_dir_content = [(parent_dir + '/' + name, hash) for name, hash in dir_content]

            add_to_dir_map(new_dir_content)
            src_hash = dir_map[src_path]
        else:
            _, src_hash = ipfs_api.add_file(event.src_path)
            add_to_dir_map([(src_path, src_hash)])

        while True:
            parent_dir = os.path.dirname(src_path)
            if not parent_dir:
                break
            parent_dir_hash = dir_map[parent_dir]
            logger.debug("Adding link to (%s, %s) from (%s, %s)" % (os.path.basename(src_path), src_hash, parent_dir, parent_dir_hash))
            new_parent_dir_hash = ipfs_api.add_link(parent_dir_hash, os.path.basename(src_path), src_hash)
            dir_map[parent_dir] = new_parent_dir_hash
            logger.debug("%s: %s" % (parent_dir, dir_map[parent_dir]))
            src_path = parent_dir
            src_hash = dir_map[parent_dir]

        ipfs_api.ls(dir_map[path])


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    ipfs_api = IPFSApi()
    # dir_content = ipfs_api.add_dir(path, recursive=True)

    add_to_dir_map(ipfs_api.add_dir(path, recursive=True))

    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()