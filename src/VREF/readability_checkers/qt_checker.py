from base_checker import ReadabilityChecker


class QtChecker(ReadabilityChecker):
    readability = """
        ram*
    """.split()

    expected_extension = '.py'

    def match(self):
        code = '' # TODO need to read contents of the file using git hashes
        return (super(QtChecker, self).match() and
            any('PySide' in line for line in code))
