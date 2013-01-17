import os


class ReadabilityChecker(object):
    readability = []

    def __init__(self, file_path, file_contents):
        self.file_path = file_path
        self.file_contents = file_contents

    def match(self):
        _, extension = os.path.splitext(self.file_path)

        return extension == self.expected_extension

    def accepted(self, accepted_by):
        "Return True if at least one of the accepting users has readability"
        with_readability = set([user.strip('*') for user in self.readability])

        return True if set(accepted_by) & with_readability else False
