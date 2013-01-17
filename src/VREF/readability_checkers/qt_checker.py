from base_checker import ReadabilityChecker
from git_tools import git_readfile


class QtChecker(ReadabilityChecker):
    readability = """
        ram*
    """.split()

    expected_extension = '.py'

    def match(self):
        return (super(QtChecker, self).match() and
                'PySide' in git_readfile(self.path, commit_hash=self.commit_hash))
