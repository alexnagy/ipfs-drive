import json


class Content:
    def __init__(self, logger):
        self._logger = logger
        self._content = {}

    def add(self, path, hash):
        self._content[path] = hash
        self._logger.debug("Added %s: %s to content" % (path, hash))

    def add_list(self, content_list):
        for path, hash in content_list:
            self.add(path, hash)

    def remove(self, path):
        hash = self._content.pop(path)
        self._logger.debug("Removed %s: %s from content" % (path, hash))

    def __getitem__(self, item):
        return self._content.get(item, None)

    def __repr__(self):
        return json.dumps(self._content, indent=4)
