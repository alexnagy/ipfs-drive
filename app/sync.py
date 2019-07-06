import os
import shutil
import base64
import logging
import time

from file import File
from directory import Directory
from observable import Observable


class Sync(Observable):
    def __init__(self, root_dir, working_dir, content, db, ipfs_client, cipher):
        super().__init__()
        self._root_dir = root_dir
        self._working_dir = working_dir
        self._content = content
        self._db = db
        self._ipfs_client = ipfs_client
        self._cipher = cipher
        self._stream = self._db.get_stream(self._stream_handler)
        self._should_listen = False
        self._logger = logging.getLogger()

    def start_listening(self):
        self._should_listen = True

    def start(self):
        db_content = self._db.get_content()
        if db_content is None:
            return

        content = {v: k for k, v in db_content.items()}
        self._download(content)

    def _download(self, content):
        cwd = os.getcwd()
        os.chdir(self._working_dir)

        for multihash in content.keys():
            self._ipfs_client.get(multihash)

        for multihash in os.listdir(self._working_dir):
            name = base64.b64decode(content[multihash]).decode()
            os.rename(multihash, name)
            full_path = os.path.join(self._working_dir, name)

            self._content.add(full_path, multihash)

            if os.path.isfile(full_path):
                File(full_path).decrypt_content(cipher=self._cipher, dst_dir=self._root_dir)
                time.sleep(0.1)
                os.remove(full_path)
            elif os.path.isdir(full_path):
                Directory(full_path).decrypt_content(cipher=self._cipher, dst_dir=self._root_dir)
                time.sleep(0.1)
                shutil.rmtree(full_path)

        os.chdir(cwd)

    def _stream_handler(self, message):
        self._logger.debug(message)

        if not self._should_listen:
            self._logger.debug("Not listening. Discarding the message")
            return

        self._notify()

        event = message['event']
        data = message['data']
        path = message['path'][1:]

        if not isinstance(data, str):
            return

        if event == 'put':
            full_path = os.path.join(self._root_dir, base64.b64decode(path).decode()).replace(os.sep, '/')

            if data:
                if self._content[full_path] != data:
                    self._download({data:path})
                    self._logger.debug("Downloaded %s at %s" % (full_path, time.time()))
            else:
                if self._content[full_path]:

                    if os.path.isfile(full_path):
                        os.remove(full_path)
                    elif os.path.isdir(full_path):
                        shutil.rmtree(full_path)

