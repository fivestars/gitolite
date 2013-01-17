from python_checker import PythonChecker
from javascript_checker import JavascriptChecker
from qt_checker import QtChecker
from cpp_checker import CppChecker
from html_checker import HtmlChecker


language_checkers = dict(
    qt=QtChecker,
    python=PythonChecker,
    javacript=JavascriptChecker,
    cpp=CppChecker,
    html=HtmlChecker
)
