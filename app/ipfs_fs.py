import ipfshttpclient


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