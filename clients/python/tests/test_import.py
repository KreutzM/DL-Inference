import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import repo2_client


def test_import():
    assert repo2_client
