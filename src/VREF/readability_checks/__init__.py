from python_check import PythonCheck
from javascript_check import JavascriptCheck
from qt_check import QtCheck
from cpp_check import CppCheck
from html_check import HtmlCheck


language_checks = dict(
    qt=QtCheck,
    python=PythonCheck,
    javacript=JavascriptCheck,
    cpp=CppCheck,
    html=HtmlCheck
)
