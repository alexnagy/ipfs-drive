import os
import shutil
import base64
import logging
import time
import json

from file import File
from directory import Directory


class Sync:
    def __init__(self, root_dir, working_dir, content, db, ipfs_client, cipher):
        self._root_dir = root_dir
        self._working_dir = working_dir
        self._content = content
        self._db = db
        self._ipfs_client = ipfs_client
        self._cipher = cipher
        self._stream = self._db.get_stream(self._stream_handler)
        self._logger = logging.getLogger()

    def start(self):
        self._download(self._db.get_content())

    def stop(self):
        self._stream.close()

    def _download(self, content):
        cwd = os.getcwd()
        os.chdir(self._working_dir)

        time_dict = {}

        for hash in content.values():
            t0 = time.time()
            self._ipfs_client.get(hash)
            time_dict[hash] = time.time()-t0

        content = {v: k for k, v in content.items()}

        for path in os.listdir(self._working_dir):
            t0 = time.time()

            hash = path
            decoded_name = base64.b64decode(content[path]).decode()
            os.rename(path, decoded_name)
            path = decoded_name
            full_path = os.path.join(self._working_dir, path)

            if os.path.isfile(full_path):
                File(full_path).decrypt_content(self._cipher, self._root_dir)
                os.remove(full_path)
            elif os.path.isdir(full_path):
                Directory(full_path).decrypt_content(self._cipher, self._root_dir)
                shutil.rmtree(full_path)

            time_dict[hash] += time.time() - t0

        self._logger.debug("Sync time:\n %s" % json.dumps(time_dict, indent=4))

        os.chdir(cwd)

    def _stream_handler(self, message):
        self._logger.debug(message)

        event = message['event']
        data = message['data']
        path = message['path'][1:]

        if not isinstance(data, str):
            return

        if event == 'put':
            if data:
                if self._content[path] != data:
                    self._download(dict(path=data))
                    self._logger.debug("Downloaded %s at %s" % (path, time.time()))
            else:
                if self._content[path]:
                    full_path = os.path.join(self._root_dir, path)
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    elif os.path.isdir(full_path):
                        shutil.rmtree(full_path)





