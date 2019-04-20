import ipfsapi
import os
import json

from encryption.aes_cipher import AESCipher
from directory import Directory


class IPFSClient:
    def __init__(self, logger):
        self._logger = logger
        self._conn = ipfsapi.connect('127.0.0.1', 5001)
        self._aes = AESCipher('parola')
        self._working_dir = os.path.join(os.getcwd(), 'working_dir')
        if not os.path.isdir(self._working_dir):
            os.mkdir(self._working_dir)

    def add_file(self, file_path, encrypted=True):
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        res = self._conn.add(file_path)
        self._logger.info("Added %s to IPFS" % file_path)
        self._logger.debug(json.dumps(res, indent=4))
        return res['Name'], res['Hash']

    def add_dir(self, dir_path, recursive, encrypted=True):
        if not os.path.exists(dir_path):
            raise FileNotFoundError(dir_path)

        if encrypted:
            encrypted_dir_path = Directory(dir_path).encrypt_content(self._aes, self._working_dir)
            dir_path = os.path.join(os.path.dirname(encrypted_dir_path), os.path.basename(dir_path))
            os.rename(encrypted_dir_path, dir_path)

        self._logger.debug("Adding %s to IPFS" % dir_path)

        resp = self._conn.add(dir_path, recursive)

        self._logger.info("Added %s to IPFS" % dir_path)
        self._logger.debug(json.dumps(resp, indent=4))

        if encrypted:
            os.rmdir(dir_path)

        if isinstance(resp, list):
            return [(d['Name'], d['Hash']) for d in resp]
        elif isinstance(resp, dict):
            return [(resp['Name'], resp['Hash'])]
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
