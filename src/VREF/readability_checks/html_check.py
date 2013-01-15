from base_check import ReadabilityCheck


class HtmlCheck(ReadabilityCheck):
    readability = """
        msu*
    """

    expected_extension = '.html'
