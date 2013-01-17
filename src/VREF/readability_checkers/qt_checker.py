from base_checker import ReadabilityChecker


class QtChecker(ReadabilityChecker):
    readability = """
        ram*
    """.split()

    expected_extension = '.py'

    def match(self):
        return (super(QtChecker, self).match() and
                'PySide' in self.file_contents)
