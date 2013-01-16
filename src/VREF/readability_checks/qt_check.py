from base_check import ReadabilityCheck


class QtCheck(ReadabilityCheck):
    readability = """
        ram*
    """.split()

    expected_extension = '.py'

    def match(self):
        if super(QtCheck, self).match():
            with open(self.path) as code:
                return any('PySide' in line for line in code.readlines())

        return False
