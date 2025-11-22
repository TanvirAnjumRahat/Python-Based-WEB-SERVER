#!/usr/bin/env python
"""
PyNetLite Web Server GUI Launcher
Run this file to start the graphical control panel
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.webserver.gui import main

if __name__ == '__main__':
    main()
