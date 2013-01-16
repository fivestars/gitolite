from base_check import ReadabilityChecker


class PythonChecker(ReadabilityChecker):
    readability = """
        guido*
        kilian*
        kevin.yu
    """.split()

    expected_extension = '.py'
