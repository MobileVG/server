#! /usr/bin/env python
from __future__ import unicode_literals

import sys
import os
import os.path


def print_usage():
    print("Usage:")
    print("  ./start.py debug|release")

def main(argv):
    if len(argv) < 1:
        print_usage()
        return
    
    self_folder = os.path.dirname(os.path.abspath(__file__))
    os.environ['VG_ROOT'] = self_folder
    os.environ['VG_ENV'] = argv[0]
    import vg
    vg.start_server()

if __name__ == '__main__':
    main(sys.argv[1:])



