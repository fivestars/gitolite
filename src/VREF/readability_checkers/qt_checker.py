from base_check import ReadabilityChecker


class QtChecker(ReadabilityChecker):
    readability = """
        ram*
    """.split()

    expected_extension = '.py'

    def match(self):
        if super(QtChecker, self).match():
            with open(self.path) as code:
                return any('PySide' in line for line in code.readlines())

        return False
