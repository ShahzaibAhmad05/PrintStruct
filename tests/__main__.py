# tests/__main__.py

"""
This file runs unittests for the tool.
"""

import unittest


if __name__ == "__main__":
    unittest.TestProgram(
        module=None,              # important: don't look only in __main__.py
        argv=["unittest", "discover", "tests"],
        verbosity=2,
        failfast=True,
    )
