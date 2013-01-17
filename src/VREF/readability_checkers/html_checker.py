from base_checker import ReadabilityChecker


class HtmlChecker(ReadabilityChecker):
    readability = """
        msu*
    """

    expected_extension = '.html'
