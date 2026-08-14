"""
Pytest configuration and path setup.
"""

import sys
import os
from pathlib import Path

# Add backend and workspace root to sys.path
root_dir = Path(__file__).parent.parent
backend_dir = root_dir / "backend"

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(root_dir))
