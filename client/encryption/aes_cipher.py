import base64
import os

from encryption.cipher import Cipher
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256


class AESCipher(Cipher):
    def __init__(self, password):
        super().__init__()
        self._key = SHA256.new(password.encode('utf-8')).digest()

    # def encrypt(self, raw):
    #     raw = self._pad(raw)
    #     if isinstance(raw, str):
    #         raw = raw.encode()
    #     iv = Random.new().read(AES.block_size)
    #     cipher = AES.new(self._key, AES.MODE_CBC, iv)
    #     return base64.b64encode(iv + cipher.encrypt(raw))
    #
    # def decrypt(self, enc):
    #     enc = base64.b64decode(enc)
    #     iv = enc[:16]
    #     cipher = AES.new(self._key, AES.MODE_CBC, iv)
    #     return self._unpad(cipher.decrypt(enc[16:]))
    #
    # @staticmethod
    # def _pad(s):
    #     bs = AES.block_size
    #     return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
    #
    # @staticmethod
    # def _unpad(s):
    #     return s[0:-s[-1]]

    def encrypt_file(self, input_file, output_file):
        chunk_size = 64 * 1024
        file_size = str(os.path.getsize(input_file)).zfill(16).encode()
        iv = Random.new().read(AES.block_size)
        encryptor = AES.new(self._key, AES.MODE_CBC, iv)
        with open(input_file, 'rb') as fin:
            with open(output_file, 'wb') as fout:
                fout.write(file_size)
                fout.write(iv)
                while True:
                    chunk = fin.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % AES.block_size != 0:
                        chunk += b' ' * (AES.block_size - len(chunk) % AES.block_size)
                    fout.write(encryptor.encrypt(chunk))

    def decrypt_file(self, input_file, output_file):
        chunk_size = 64 * 1024
        with open(input_file, 'rb') as fin:
            file_size = int(fin.read(16))
            iv = fin.read(AES.block_size)
            decryptor = AES.new(self._key, AES.MODE_CBC, iv)
            with open(output_file, 'wb') as fout:
                while True:
                    chunk = fin.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    fout.write(decryptor.decrypt(chunk))
                fout.truncate(file_size)
