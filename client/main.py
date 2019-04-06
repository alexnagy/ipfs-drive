import sys
import logging
import time
import ipfsapi
import json
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


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


content_map = {}


def add_to_content_map(content_list):
    global content_map

    for name, hash in content_list:
        if name:
            content_map[name] = hash

    logger.debug(json.dumps(content_map, indent=4))


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

        logger.debug("Adding %s to IPFS" % dir_path)

        resp = self.conn.add(dir_path, recursive)

        logger.info("Added %s to IPFS" % dir_path)
        logger.debug(json.dumps(resp, indent=4))

        if isinstance(resp, list):
            return [(d['Name'], d['Hash']) for d in resp]
        elif isinstance(resp, dict):
            return [(resp['Name'], resp['Hash'])]
        else:
            raise Exception("Unhandled response instance %s!" % type(resp))

    def add_link(self, root, name, ref):
        resp = self.conn.object_patch_add_link(root, name, ref)
        logger.info("Added link to (%s, %s) from %s" % (name, ref, root))
        logger.debug(json.dumps(resp, indent=4))
        return resp['Hash']

    def rm_link(self, root, link):
        resp = self.conn.object_patch_rm_link(root, link)
        logger.info("Removed link to %s from %s" % (link, root))
        logger.debug(json.dumps(resp, indent=4))

    def ls(self, hash):
        resp = self.conn.ls(hash)
        return json.dumps(resp, indent=4)


class EventHandler(FileSystemEventHandler):
    def on_created(self, event):
        src_path = event.src_path.replace(os.sep, '/')
        logger.info("CREATED %s" % src_path)
        if os.path.isdir(src_path):
            self._on_created_dir(src_path)
        else:
            self._on_created_file(src_path)

        src_hash = content_map[src_path]

        self._add_links_to_parent_dirs(src_path, src_hash)

        logger.debug(ipfs_api.ls(content_map[path]))

    @staticmethod
    def _on_created_dir(dir_path):
        parent_dir_path = os.path.dirname(dir_path)
        dir_name = os.path.basename(dir_path)

        current_dir = os.getcwd()
        os.chdir(parent_dir_path)

        relative_dir_content = ipfs_api.add_dir(dir_name, True)

        os.chdir(current_dir)

        dir_content = [(parent_dir_path + '/' + name, hash) for name, hash in relative_dir_content]

        add_to_content_map(dir_content)

        return content_map[dir_path]

    @staticmethod
    def _on_created_file(file_path):
        _, file_hash = ipfs_api.add_file(file_path)
        add_to_content_map([(file_path, file_hash)])

    @staticmethod
    def _add_links_to_parent_dirs(src_path, src_hash):
        while os.path.dirname(src_path):
            parent_dir = os.path.dirname(src_path)
            parent_dir_hash = content_map[parent_dir]

            logger.debug("Adding link to (%s, %s) from (%s, %s)"
                         % (os.path.basename(src_path), src_hash, parent_dir, parent_dir_hash))

            new_parent_dir_hash = ipfs_api.add_link(parent_dir_hash, os.path.basename(src_path), src_hash)
            content_map[parent_dir] = new_parent_dir_hash

            logger.debug("%s: %s" % (parent_dir, content_map[parent_dir]))

            src_path = parent_dir
            src_hash = content_map[parent_dir]


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    ipfs_api = IPFSApi()

    add_to_content_map(ipfs_api.add_dir(path, recursive=True))

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
