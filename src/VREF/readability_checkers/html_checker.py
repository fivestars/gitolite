from base_check import ReadabilityChecker


class HtmlChecker(ReadabilityChecker):
    readability = """
        msu*
    """

    expected_extension = '.html'
