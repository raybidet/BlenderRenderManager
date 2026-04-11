#!/usr/bin/env python
"""Run tests for Juice Render Manager."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_drag_drop import DragDropTests
from unittest import main

if __name__ == "__main__":
    main(verbosity=2)
