import os


class ReadabilityCheck:
    readability = []

    def __init__(file_path):
        self.path = file_path

    def match(self):
        if not self.hasattr('expected_extension'):
            raise Exception('Implement in specific class')

        _, extension = os.path.splitext(self.path)

        return extension == expected_extension

    def __call__(self, accepting_users):
        "Return True if at least one of the accepting users has readability"
        with_readability = set([user.strip('*') for user in readability])

        return True if set(accepting_users) & with_readability else False
