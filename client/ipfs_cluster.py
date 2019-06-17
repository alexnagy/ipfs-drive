import requests
import random
import logging


class IPFSCluster:
    def __init__(self):
        self._peers = ['40.78.159.206', '23.99.201.242', '40.77.30.228']
        self._logger = logging.getLogger()

    def pin(self, multihash):
        for _ in range(5):
            url = r'http://%s:9094/pins/%s' % (random.choice(self._peers), multihash)
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

    def unpin(self, multihash):
        for _ in range(5):
            url = r'http://%s:9094/pins/%s' % (random.choice(self._peers), multihash)
            try:
                response = requests.delete(url, timeout=5)
                response.raise_for_status()
            except requests.HTTPError as http_err:
                self._logger.error(http_err)
            except Exception as err:
                self._logger.error(err)
            else:
                self._logger.info("Unpinned %s from cluster" % multihash)
                break