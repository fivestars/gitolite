from base_check import ReadabilityCheck


class JavascriptCheck(ReadabilityCheck):
    readability = """
        ram*
    """.split()

    expected_extension = '.js'
