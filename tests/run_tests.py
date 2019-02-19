#!/usr/bin/env python3

import pytest
import sys, os


def main():
    pytest_cmd = ["-s", "-v", "--tb=short", "--show-capture=no"]
    pytest.main(pytest_cmd)


if __name__ == "__main__":
    # Add the root directory to 'sys.path' so the tests can find the 'src' directory
    dir_name = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, dir_name + '/../')

    main()
