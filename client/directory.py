import os
import shutil

from file import File


class Directory:
    def __init__(self, path):
        if not os.path.isdir(path):
            raise Exception("%s is not a directory!" % path)
        self._path = path
        self._parent = os.path.dirname(self._path)
        self._name = os.path.basename(self._path)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    def remove(self):
        shutil.rmtree(self._path)

    def ls(self, recursive=False):
        content = []

        if recursive:
            for root, subdirs, files in os.walk(self._path):
                for dir in subdirs:
                    content.append(os.path.join(root, dir))
                for file in files:
                    content.append(os.path.join(root, file))
        else:
            for el in os.listdir(self._path):
                content.append(os.path.join(self._path, el))

        return content

    def create_structure_copy(self, dst):
        prev_cwd = os.getcwd()
        os.chdir(self._parent)

        for root, subdirs, files in os.walk(self._name):
            structure = os.path.join(dst, root[len(self._name)+1:])
            if not os.path.isdir(structure):
                os.mkdir(structure)

        os.chdir(prev_cwd)

    def encrypt_content(self, cipher, dst_dir):
        encypted_dir_path = os.path.join(dst_dir, self._name)

        prev_cwd = os.getcwd()
        os.chdir(self._parent)

        for root, subdirs, files in os.walk(self._name):
            encrypted_root = os.path.join(encypted_dir_path, root[len(self._name) + 1:])
            if not os.path.isdir(encrypted_root):
                os.mkdir(encrypted_root)
            for file in files:
                file_path = os.path.join(self._parent, root, file).replace(os.sep, '/')
                File(file_path).encrypt_content(cipher, encrypted_root)

        os.chdir(prev_cwd)

        return encypted_dir_path

    def decrypt_content(self, cipher, dst_dir):
        decrypted_dir_path = os.path.join(dst_dir, self._name + '_decrypted')

        prev_cwd = os.getcwd()
        os.chdir(self._parent)

        for root, subdirs, files in os.walk(self._name):
            decrypted_root = os.path.join(decrypted_dir_path, root[len(self._name) + 1:])
            if not os.path.isdir(decrypted_root):
                os.mkdir(decrypted_root)
            for file in files:
                encrypted_file_path = os.path.join(root, file)
                file_path = os.path.join(decrypted_root, file)
                cipher.decrypt_file(encrypted_file_path, file_path)

        os.chdir(prev_cwd)

        return decrypted_dir_path
