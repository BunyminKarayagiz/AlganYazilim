import argparse
from argparse import ArgumentParser

import path
import time
try:
    parser = argparse.ArgumentParser()
    parser.add_argument('--connect', default='tcp:127.0.0.1:5762')
    args = parser.parse_args()
    connection_string = args.connect
    iha=path.Plane(connection_string)
    while True:
        print(iha.pos_alt_rel)
        time.sleep(1)
except KeyboardInterrupt as e:
    print(e)
    pass