import ipfshttpclient
import os
import json
import logging
import requests
import random


class IPFSClient:
    def __init__(self, cipher, working_dir):
        self._cipher = cipher
        self._working_dir = working_dir
        if not os.path.isdir(self._working_dir):
            os.mkdir(self._working_dir)
        self._logger = logging.getLogger()

    def add_file(self, file, encrypted=True):
        if not os.path.exists(file.path):
            raise FileNotFoundError(file.path)

        original_file_path = file.path
        if encrypted:
            encrypted_file_path = file.encrypt_content(self._cipher, self._working_dir)
            file.path = encrypted_file_path.replace(os.sep, '/')

        with ipfshttpclient.connect() as client:
            resp = client.add(file.path)

        self._logger.info("Added %s to IPFS" % file.path)
        self._logger.debug(json.dumps(resp, indent=4))

        if encrypted:
            file.remove()
            file.path = original_file_path

        self.pin_to_cluster(resp['Hash'])

        return resp['Hash']

    def add_dir(self, dir, recursive, encrypted=True):
        if not os.path.exists(dir.path):
            raise FileNotFoundError(dir.path)

        original_dir_path = dir.path
        if encrypted:
            encrypted_dir_path = dir.encrypt_content(self._cipher, self._working_dir)
            dir.path = encrypted_dir_path.replace(os.sep, '/')

        with ipfshttpclient.connect() as client:
            resp = client.add(dir.path)

        self._logger.info("Added %s to IPFS" % dir.path)
        self._logger.debug(json.dumps(resp, indent=4))

        if encrypted:
            dir.remove()
            dir.path = original_dir_path

        if isinstance(resp, list):
            return_list = []
            for d in resp:
                if d['Name'] == os.path.basename(dir.path):
                    self.pin_to_cluster(d['Hash'])
                return_list.append((os.path.join(os.path.dirname(dir.path), d['Name']).replace(os.sep, '/'), d['Hash']))
            return return_list
        elif isinstance(resp, dict):
            self.pin_to_cluster(resp['Hash'])
            return [(os.path.join(os.path.dirname(dir.path), resp['Name']).replace(os.sep, '/'), resp['Hash'])]
        else:
            raise Exception("Unhandled response instance %s!" % type(resp))

    def add_link(self, root, name, ref):
        with ipfshttpclient.connect() as client:
            resp = client.object.patch.add_link(root, name, ref)
        self._logger.info("Added link to (%s, %s) from %s" % (name, ref, root))
        self._logger.debug(json.dumps(resp, indent=4))
        return resp['Hash']

    def rm_link(self, root, ref):
        with ipfshttpclient.connect() as client:
            resp = client.object.patch.rm_link(root, ref)
        self._logger.info("Removed link to %s from %s" % (ref, root))
        self._logger.debug(json.dumps(resp, indent=4))
        return resp['Hash']

    def ls(self, hash):
        with ipfshttpclient.connect() as client:
            resp = client.ls(hash)

        return json.dumps(resp, indent=4)

    def get(self, hash):
        with ipfshttpclient.connect() as client:
            client.get(hash)

    def pin_to_cluster(self, multihash):
        clusters = ['40.78.159.206', '104.43.141.191', '40.77.30.228']
        url = r'http://%s:9094/pins/%s' % (random.choice(clusters), multihash)

        for _ in range(5):
            try:
                response = requests.post(url, timeout=5)
                response.raise_for_status()
            except requests.HTTPError as http_err:
                self._logger.error(http_err)
            except Exception as err:
                self._logger.error(err)
            else:
                self._logger.info("Pinned %s to cluster" % multihash)
                break
