"""
Files utils.
"""

import base64
import io
import os
import json
from os.path import exists, join
from typing import Any, List, Union

try:
    from .rttm import str2list, list2str
except ImportError:
    pass


def open_json(
    file_name: str, path_save: str = None, create_if_not_exist: bool = False
) -> Union[dict, None]:
    """
    Open and read data from json file.

    Parameters
    ----------
    file_name: str
        Name of json file.
    path_save: str
        Path to json file.
    create_if_not_exist: str
        Create json file if not exist.

    Returns
    -------
    data: Union[dict, None]
        Loaded dict from json file or None if file not exist.
    """
    if not path_save:
        path_save = file_name
    else:
        path_save = join(path_save, file_name)

    if exists(path_save):
        return json.loads(open(path_save, "r", encoding="utf8").read())

    elif create_if_not_exist:
        open(path_save, "w").write(json.dumps({}))
        return None

    else:
        return None


def save_json(file_name: str, file_data: dict, path_save: str = None):
    """
    Open and save json data to json file.

    Parameters:
        file_name (str):
            Name of json file or full path.

        file_data (dict):
            Json data to write.

        path_save (str):
            Path to save without file name.
    """
    if not path_save:
        path_save = file_name
    else:
        path_save = join(path_save, file_name)

    with open(path_save, "w", encoding="utf8") as json_file:
        json_file.write(
            json.dumps(file_data, indent=4, sort_keys=True, ensure_ascii=False)
        )


def save_list_rttm(file_name: str, rttm: list, path_save: str = None):
    """
    Open and save rttm list data to text-like file.

    Args
    ----------
        `file_name` : name of rttm file or full path.

        `rttm` : list rttm data.

        `path_save` (opt): path to file to save without file name.
    """
    if not path_save:
        path_save = file_name
    else:
        path_save = join(path_save, file_name)

    str_rttm = list2str(rttm)
    with open(path_save, "w") as f:
        f.write(str_rttm)


def open_list_rttm(
    file_name: str, path_save: str = None, create_if_not_exist: bool = False
):
    """
    Open and read list rttm from text-like rttm file.

    Args
    ----------
        `file_name` : name of rttm file.

        `path_save` (opt): path to rttm file.

        `create_if_not_exist` (opt=False): create rttm file if not exist.

    Return
    ----------
        `List[List[str]]` : loaded list rttm from rttm file or None if file not exist.
    """
    if not path_save:
        path_save = file_name
    else:
        path_save = join(path_save, file_name)

    if exists(path_save):
        str_rttm = ""
        with open(path_save, "r") as f:
            str_rttm = f.read()
        return str2list(str_rttm)

    elif create_if_not_exist:
        with open(path_save, "w") as f:
            f.write("")
        return None

    else:
        return None


def load_env_file(dotenv_path, override=True):
    with open(dotenv_path) as file_obj:
        lines = file_obj.read().splitlines()  # Removes \n from lines

    dotenv_vars = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        dotenv_vars.setdefault(key, value)

    if override:
        os.environ.update(dotenv_vars)
    else:
        for key, value in dotenv_vars.items():
            os.environ.setdefault(key, value)


def check_file(file: Any):
    if type(file) == io.BytesIO:
        return io.BytesIO(file.getvalue())
    else:
        return file


def convert_from(data: Any, convert: List[str]):
    if len(convert) != 0:
        for conv_type in convert:
            if conv_type == "base64":
                data = base64.b64decode(data.encode("utf-8"))
            elif conv_type == "json":
                data = json.loads(data)
    return data


def convert_to(data: Any, convert: List[str]):
    if len(convert) != 0:
        for conv_type in convert:
            if conv_type == "base64":
                data = base64.b64encode(data).decode("utf-8")
            elif conv_type == "json":
                data = json.dumps(data)
    return data
