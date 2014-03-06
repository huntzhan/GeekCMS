import os.path
import unittest


def additional_tests():
    loader = unittest.defaultTestLoader
    start_dir = os.getcwd()
    suites = loader.discover(start_dir)
    return suites
