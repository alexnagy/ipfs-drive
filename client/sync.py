import os
import shutil
import base64

from file import File
from directory import Directory


class Sync:
    def __init__(self, root_dir, working_dir, db, ipfs_client, cipher, logger):
        self._root_dir = root_dir
        self._working_dir = working_dir
        self._db = db
        self._ipfs_client = ipfs_client
        self._cipher = cipher
        self._logger = logger

    def sync(self):
        cwd = os.getcwd()
        os.chdir(self._working_dir)

        content = self._db.get_content()
        for hash in content.values():
            self._ipfs_client.get(hash)

        content = {v: k for k, v in content.items()}

        for path in os.listdir(self._working_dir):
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

        os.chdir(cwd)

