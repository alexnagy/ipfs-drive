import ipfshttpclient
import os
from nt import scandir


# with ipfshttpclient.connect() as conn:
#     resp = conn.ls(r'QmYGcpuNranX82S2sDXLrwsKizZ3Q8A6xSJBEn5rgosUb8')
#     print(len(resp['Objects']))


class IPFSFile:
    def __init__(self, name, multihash, parent=None):
        self._name = name
        self._multihash = multihash
        self._parent = parent

    @property
    def name(self):
        return self._name

    @property
    def multihash(self):
        return self._multihash

    @property
    def parent(self):
        return self._parent


class IPFSDirectory(IPFSFile):
    def __init__(self, name, multihash, parent=None):
        super().__init__(name, multihash, parent)
        self._dirs = []
        self._files = []

    @property
    def dirs(self):
        return self._dirs

    @property
    def files(self):
        return self._files

    def add_file(self, file):
        self._files.append(file)

    def add_dir(self, dir):
        self._dirs.append(dir)


# root = None
#
# for dirname, dirs, files in walk(r'QmbxTXic3iiJ23VL8urj2KHxfQTHW1WaLcq3LCHPiWy3jW', '.'):
#     root = IPFSDirectory(dirname)
#
#     for dir in dirs:
#         ipfs_dir = IPFSDirectory(dir, root)
#         root.add_dir(ipfs_dir)
#
#     for file in files:
#         ipfs_file = IPFSFile(file, root)
#         root.add_file(file)
#
# while root.parent:
#     root = root.parent
#
# print(root.files)


# def walk(multihash, name):
#     dir_links = []
#     nondir_links = []
#
#     with ipfshttpclient.connect() as conn:
#         resp = conn.ls(multihash)
#         links = resp['Objects'][0]['Links']
#
#     for link in links:
#         is_dir = link['Type'] == 1
#
#         if is_dir:
#             dir_links.append(link)
#         else:
#             nondir_links.append(link)
#
#     yield name, [link['Name'] for link in dir_links], [link['Name'] for link in nondir_links]
#
#     for link in dir_links:
#         yield from walk(link['Hash'], link['Name'])


root_dir = IPFSDirectory('.', r'QmYGcpuNranX82S2sDXLrwsKizZ3Q8A6xSJBEn5rgosUb8')


def walk(root):
    dir_links = []
    nondir_links = []

    with ipfshttpclient.connect() as conn:
        resp = conn.ls(root.multihash)
        links = resp['Objects'][0]['Links']

    for link in links:
        is_dir = link['Type'] == 1

        if is_dir:
            dir_links.append(link)
            root.add_dir(IPFSDirectory(link['Name'], link['Hash'], root))
        else:
            nondir_links.append(link)
            root.add_file(IPFSFile(link['Name'], link['Hash'], root))

    for dir in root.dirs:
        walk(dir)


# walk(root_dir)
#
# for file in root_dir.files + root_dir.dirs:
#     print(os.path.join(root_dir.name, file.name))


