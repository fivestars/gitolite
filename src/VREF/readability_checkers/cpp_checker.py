from base_checker import ReadabilityChecker


class CppChecker(ReadabilityChecker):
    readability = """
        daigo*
        harvinder
    """

    expected_extension = '.cpp'
