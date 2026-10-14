import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERS = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(VERS), "harness"))
sys.path.insert(0, VERS)
sys.path.insert(0, HERE)
