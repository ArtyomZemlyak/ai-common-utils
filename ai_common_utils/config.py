"""
Config utils.
"""

import pathlib
import os
from typing import Union
import inspect

from .files import open_json


def load_config(config: Union[str, dict] = None, level: int = 4):
    """
    Function for dynamic load config from config.json file in root of project.

    Args
    ----------
        `config` : Path to config.json file or dict with config for Varvara.

        `level` (opt=4): level of module relatively config.json file. (0 for self config.json)

    Return
    ----------
        `CONFIG` : dict data from config.json.
    """
    CONFIG = {}
    if config:
        if type(config) == dict:
            CONFIG = config
        elif type(config) == str:
            CONFIG = open_json(config)
        else:
            raise TypeError(
                "config param is a path (str) or dict with config for Varvara project!"
            )
    else:
        path_cfg = pathlib.Path(os.path.abspath(inspect.stack()[1].filename))

        for i in range(level):
            path_cfg = path_cfg.parent

        path_cfg = path_cfg.resolve()
        path_cfg = os.path.join(path_cfg, "config.json")
        CONFIG = open_json(path_cfg)

    if not CONFIG or type(CONFIG) != dict:
        raise TypeError("Config should be specified!")

    return CONFIG
