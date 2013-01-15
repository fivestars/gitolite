from base_check import ReadabilityCheck


class PythonCheck(ReadabilityCheck):
    readability = """
        guido*
        kilian*
        kevin.yu
    """.split()

    expected_extension = '.py'
