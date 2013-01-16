import os


class ReadabilityChecker:
    readability = []

    def __init__(self, file_path):
        self.path = file_path

    def match(self):
        if not self.hasattr('expected_extension'):
            raise Exception('Implement in specific class')

        _, extension = os.path.splitext(self.path)

        return extension == expected_extension

    def accepted(self, accepted_by):
        "Return True if at least one of the accepting users has readability"
        with_readability = set([user.strip('*') for user in self.readability])

        return True if set(accepted_by) & with_readability else False
