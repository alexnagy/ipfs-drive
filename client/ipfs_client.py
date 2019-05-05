import ipfsapi
import os
import json


class IPFSClient:
    def __init__(self, cipher, working_dir, logger):
        self._cipher = cipher
        self._working_dir = working_dir
        if not os.path.isdir(self._working_dir):
            os.mkdir(self._working_dir)
        self._logger = logger
        self._conn = ipfsapi.connect('127.0.0.1', 5001)

    def add_file(self, file, encrypted=True):
        if not os.path.exists(file.path):
            raise FileNotFoundError(file.path)

        original_file_path = file.path
        if encrypted:
            encrypted_file_path = file.encrypt_content(self._cipher, self._working_dir)
            file.path = encrypted_file_path.replace(os.sep, '/')

        resp = self._conn.add(file.path)

        self._logger.info("Added %s to IPFS" % file.path)
        self._logger.debug(json.dumps(resp, indent=4))

        if encrypted:
            file.remove()
            file.path = original_file_path

        return resp['Hash']

    def add_dir(self, dir, recursive, encrypted=True):
        if not os.path.exists(dir.path):
            raise FileNotFoundError(dir.path)

        original_dir_path = dir.path
        if encrypted:
            encrypted_dir_path = dir.encrypt_content(self._cipher, self._working_dir)
            dir.path = encrypted_dir_path.replace(os.sep, '/')

        resp = self._conn.add(dir.path, recursive)

        self._logger.info("Added %s to IPFS" % dir.path)
        self._logger.debug(json.dumps(resp, indent=4))

        if encrypted:
            dir.remove()
            dir.path = original_dir_path

        if isinstance(resp, list):
            return [(os.path.join(os.path.dirname(dir.path), d['Name']).replace(os.sep, '/'), d['Hash']) for d in resp]
        elif isinstance(resp, dict):
            return [(os.path.join(os.path.dirname(dir.path), resp['Name']).replace(os.sep, '/'), resp['Hash'])]
        else:
            raise Exception("Unhandled response instance %s!" % type(resp))

    def add_link(self, root, name, ref):
        resp = self._conn.object_patch_add_link(root, name, ref)
        self._logger.info("Added link to (%s, %s) from %s" % (name, ref, root))
        self._logger.debug(json.dumps(resp, indent=4))
        return resp['Hash']

    def rm_link(self, root, ref):
        resp = self._conn.object_patch_rm_link(root, ref)
        self._logger.info("Removed link to %s from %s" % (ref, root))
        self._logger.debug(json.dumps(resp, indent=4))
        return resp['Hash']

    def ls(self, hash):
        resp = self._conn.ls(hash)

        return json.dumps(resp, indent=4)

    def get(self, hash):
        self._conn.get(hash)
