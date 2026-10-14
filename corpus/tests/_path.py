"""Puts corpus/ on sys.path for the tests (imported first by every test file)."""
import os
import sys

CORPUS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(CORPUS)
if CORPUS not in sys.path:
    sys.path.insert(0, CORPUS)
