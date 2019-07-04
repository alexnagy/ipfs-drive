import json
import os
import logging

from observable import Observable


class Content(Observable):
    def __init__(self, root_dir, db):
        super().__init__()
        self._root_dir = root_dir
        self._db = db
        self._logger = logging.getLogger()
        self._content = {}

    def add(self, path, hash):
        self._content[path] = hash
        if os.path.relpath(path, self._root_dir) == os.path.basename(path):
            self._db.add_content(os.path.basename(path), hash)
        self._logger.debug("Added %s: %s to content" % (path, hash))
        self._notify()

    def add_list(self, content_list):
        for path, hash in content_list:
            self.add(path, hash)

    def remove(self, path):
        hash = self._content.pop(path)
        if os.path.relpath(path, self._root_dir) == os.path.basename(path):
            self._db.remove_content(os.path.basename(path))
        self._logger.debug("Removed %s: %s from content" % (path, hash))
        self._notify()

    def contains(self, path):
        return path in self._content

    def __getitem__(self, item):
        return self._content.get(item, None)

    def __repr__(self):
        return json.dumps(self._content, indent=4)
