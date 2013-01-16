from base_check import ReadabilityChecker


class JavascriptChecker(ReadabilityChecker):
    readability = """
        ram*
    """.split()

    expected_extension = '.js'
