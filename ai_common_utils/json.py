"""
JSON utils.
"""

import json
import logging
from typing import Any


try:
    import numpy as np

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, float):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

except ImportError:
    logging.error("Numpy not installed. json.NumpyEncoder not allowed!")


def open_json(path: str):
    return json.loads(open(path, "r", encoding="utf8").read())


def save_json(data: Any, path: str):
    with open(path, "w", encoding="utf8") as json_file:
        json_file.write(
            json.dumps(
                data,
                indent=4,
                sort_keys=True,
                ensure_ascii=False,
            )
        )
        json_file.close()
