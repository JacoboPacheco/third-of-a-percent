import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ENV), "harness"))
sys.path.insert(0, ENV)
sys.path.insert(0, HERE)
