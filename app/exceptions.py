class EmailExistsException(Exception):
    def __init__(self):
        super().__init__()


class InvalidEmailException(Exception):
    def __init__(self):
        super().__init__()


class InvalidPasswordException(Exception):
    def __init__(self):
        super().__init__()


class WeakPasswordException(Exception):
    def __init__(self):
        super().__init__()