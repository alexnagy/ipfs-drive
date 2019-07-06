class Observer:
    def __init__(self):
        self._subject = None

    def update(self, *args):
        raise NotImplementedError
