from base_checker import ReadabilityChecker


class JavascriptChecker(ReadabilityChecker):
    readability = """
        ram*
    """.split()

    expected_extension = '.js'
