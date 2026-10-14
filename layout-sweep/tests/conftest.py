import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SWEEP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(SWEEP), "harness"))
sys.path.insert(0, SWEEP)
sys.path.insert(0, HERE)
