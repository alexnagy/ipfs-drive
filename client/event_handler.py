import os
from watchdog.events import FileSystemEventHandler

from encryption.aes_cipher import AESCipher


class EventHandler(FileSystemEventHandler):
    def __init__(self, ipfs_client, content, root_dir, logger):
        super().__init__()
        self._ipfs_client = ipfs_client
        self._content = content
        self._root_dir = root_dir
        self._logger = logger
        self._aes = AESCipher('parola')
    
    def on_created(self, event):
        src_path = event.src_path.replace(os.sep, '/')
        self._on_created(src_path)
        self._logger.debug("Root dir hash: %s" % self._content[self._root_dir])

    def on_deleted(self, event):
        src_path = event.src_path.replace(os.sep, '/')
        self._on_deleted(src_path)
        self._logger.debug("Root dir hash: %s" % self._content[self._root_dir])

    def on_modified(self, event):
        if os.path.isdir(event.src_path):
            return

        file_path = event.src_path.replace(os.sep, '/')

        self._logger.info("Modified %s" % file_path)

        parent_dir_path = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        # add modified file to ipfs
        _, file_hash = self._ipfs_client.add_file(file_path)

        # replace modified file in content
        self._content.add(file_path, file_hash)

        # remove link from parent to the file before being modified
        self._ipfs_client.rm_link(self._content[parent_dir_path], file_name)

        # add link from parent to the file after being modified
        new_parent_dir_hash = self._ipfs_client.add_link(self._content[parent_dir_path], file_name, file_hash)

        # add new parent link to self._content
        self._content.add(parent_dir_path, new_parent_dir_hash)

        # add link from parent dirs to the updated parent dir of the modified file
        self._add_links_to_parent_dirs(parent_dir_path, self._content[parent_dir_path])

        self._logger.debug("Root dir hash: %s" % self._content[self._root_dir])

    def on_moved(self, event):
        src_path = event.src_path.replace(os.sep, '/')
        dst_path = event.dest_path.replace(os.sep, '/')

        self._logger.debug("Moved %s to %s" % (src_path, dst_path))

        # create dst
        self._on_created(dst_path)

        # delete src
        self._on_deleted(src_path)

        self._logger.debug("Root dir hash: %s" % self._content[self._root_dir])

    def _on_created(self, src_path):
        self._logger.info("Created %s" % src_path)

        if os.path.isdir(src_path):
            self._on_created_dir(src_path)
        else:
            self._on_created_file(src_path)

        src_hash = self._content[src_path]

        self._add_links_to_parent_dirs(src_path, src_hash)

    def _on_created_dir(self, dir_path):
        parent_dir_path = os.path.dirname(dir_path)
        dir_name = os.path.basename(dir_path)

        current_dir = os.getcwd()
        os.chdir(parent_dir_path)

        relative_dir_content = self._ipfs_client.add_dir(dir_name, True)

        os.chdir(current_dir)

        dir_content = [(parent_dir_path + '/' + name, hash) for name, hash in relative_dir_content]

        self._content.add_list(dir_content)

        return self._content[dir_path]

    def _on_created_file(self, file_path):
        _, file_hash = self._ipfs_client.add_file(file_path)
        self._content.add(file_path, file_hash)

    def _add_links_to_parent_dirs(self, src_path, src_hash):
        while os.path.dirname(src_path):
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

    def _on_deleted(self, src_path):
        self._logger.info("Deleted %s" % src_path)

        parent_dir_path = os.path.dirname(src_path)

        if self._content[parent_dir_path] is None:
            return

        new_parent_dir_hash = self._ipfs_client.rm_link(self._content[parent_dir_path], os.path.basename(src_path))

        self._content.add(parent_dir_path, new_parent_dir_hash)
        self._content.remove(src_path)

        self._add_links_to_parent_dirs(parent_dir_path, self._content[parent_dir_path])