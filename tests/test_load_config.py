from os import path
import sys

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from ai_common_utils.config import load_config


def test_load_config():
    assert load_config(level=1) == {"test": True}
