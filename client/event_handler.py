import os
import logging
import time

from watchdog.events import FileSystemEventHandler
from directory import Directory
from file import File


class EventHandler(FileSystemEventHandler):
    def __init__(self, ipfs_client, ipfs_cluster, content, root_dir):
        super().__init__()
        self._ipfs_client = ipfs_client
        self._ipfs_cluster = ipfs_cluster
        self._content = content
        self._root_dir = root_dir
        self._logger = logging.getLogger()
    
    def on_created(self, event):
        src_path = event.src_path.replace(os.sep, '/')
        self._on_created(src_path)

    def on_deleted(self, event):
        src_path = event.src_path.replace(os.sep, '/')
        self._on_deleted(src_path)

    def on_modified(self, event):
        if os.path.isdir(event.src_path):
            return

        file = File(event.src_path.replace(os.sep, '/'))

        self._logger.info("Modified %s" % file.path)

        parent_dir_path = os.path.dirname(file.path)
        file_name = os.path.basename(file.path)

        # add modified file to ipfs
        file.multihash = self._ipfs_client.add_file(file)

        self._ipfs_cluster.pin(file.multihash)

        # replace modified file in content
        self._content.add(file.path, file.multihash)

        if self._content.contains(parent_dir_path):
            # remove link from parent to the file before being modified
            self._ipfs_client.rm_link(self._content[parent_dir_path], file_name)

            # add link from parent to the file after being modified
            new_parent_dir_hash = self._ipfs_client.add_link(self._content[parent_dir_path], file_name, file.multihash)

            # add new parent link to self._content
            self._content.add(parent_dir_path, new_parent_dir_hash)

            # add link from parent dirs to the updated parent dir of the modified file
            self._add_links_to_parent_dirs(parent_dir_path, self._content[parent_dir_path])

    def on_moved(self, event):
        src_path = event.src_path.replace(os.sep, '/')
        dst_path = event.dest_path.replace(os.sep, '/')

        self._logger.debug("Moved %s to %s" % (src_path, dst_path))

        # create dst
        self._on_created(dst_path)

        # delete src
        self._on_deleted(src_path)

    def _on_created(self, src_path):
        self._logger.info("Created %s at %s" % (src_path, time.time()))

        if os.path.isdir(src_path):
            if not os.listdir(src_path):
                return
            self._content.add_list(self._ipfs_client.add_dir(Directory(src_path)))
        else:
            file = File(src_path)
            file.multihash = self._ipfs_client.add_file(file)

            self._content.add(file.path, file.multihash)

        src_hash = self._content[src_path]

        self._add_links_to_parent_dirs(src_path, src_hash)

    def _add_links_to_parent_dirs(self, src_path, src_hash):
        while self._content[os.path.dirname(src_path)]:
            parent_dir = os.path.dirname(src_path)
            parent_dir_hash = self._content[parent_dir]

            if parent_dir_hash is None:
                break

            self._logger.debug("Adding link to (%s, %s) from (%s, %s)"
                               % (os.path.basename(src_path), src_hash, parent_dir, parent_dir_hash))

            new_parent_dir_hash = self._ipfs_client.add_link(parent_dir_hash, os.path.basename(src_path), src_hash)
            self._content.add(parent_dir, new_parent_dir_hash)

            self._logger.debug("%s: %s" % (parent_dir, self._content[parent_dir]))

            src_path = parent_dir
            src_hash = self._content[parent_dir]

        self._ipfs_cluster.pin(src_hash)

    def _on_deleted(self, src_path):
        self._logger.info("Deleted %s" % src_path)

        parent_dir_path = os.path.dirname(src_path)

        if self._content[parent_dir_path] is None:
            self._ipfs_cluster.unpin(self._content[src_path])
            self._content.remove(src_path)
            return

        new_parent_dir_hash = self._ipfs_client.rm_link(self._content[parent_dir_path], os.path.basename(src_path))

        self._content.add(parent_dir_path, new_parent_dir_hash)
        self._content.remove(src_path)

        self._add_links_to_parent_dirs(parent_dir_path, self._content[parent_dir_path])