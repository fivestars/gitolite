from base_check import ReadabilityChecker


class CppChecker(ReadabilityChecker):
    readability = """
        daigo*
        harvinder
    """

    expected_extension = '.cpp'
