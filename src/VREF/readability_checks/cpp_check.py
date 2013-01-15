from base_check import ReadabilityCheck


class CppCheck(ReadabilityCheck):
    readability = """
        daigo*
        harvinder
    """

    expected_extension = '.cpp'
