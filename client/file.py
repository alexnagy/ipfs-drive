import os


class File:
    def __init__(self, path):
        if not os.path.isfile(path):
            raise Exception("%s is not a file!" % path)
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
        os.remove(self._path)

    def encrypt_content(self, cipher, dst_dir):
        encrypted_file_path = os.path.join(dst_dir, self._name)

        cwd = os.getcwd()
        os.chdir(self._parent)

        cipher.encrypt_file(self._path, encrypted_file_path)

        os.chdir(cwd)

        return encrypted_file_path

    def decrypt_content(self, cipher, dst_dir):
        decrypted_file_path = os.path.join(dst_dir, self._name)

        cwd = os.getcwd()
        os.chdir(self._parent)

        cipher.decrypt_file(self._path, decrypted_file_path)

        os.chdir(cwd)

        return decrypted_file_path
