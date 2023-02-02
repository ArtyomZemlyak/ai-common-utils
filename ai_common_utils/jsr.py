"""
JSR file utils.

JSR - JSON Speech Recognition file.

filename.jsr.json

JSR file format:
```python
[
    replica_1,
    replica_2,
    replica_3,
    ...
]
```

Replica format:
```python
{
    "idx": str - opt, special index if needed,
    "speaker": {
        "idx": str,
        "display_name": str, - opt
        "conf": float
    },
    "speech": {
        "time_start": float - time in seconds, when replica started,
        "end_time": float - time in seconds, when replica ended,
        "duration": float - time in seconds, duration of this replica,
        "tokens": [
            {
                "start: float - time in seconds, when word started,
                "end": float - time in seconds, when word ended,
                "word": str,
                "conf": float
            },
            ...
        ],
        "text": str,
        "conf": float
    },
    "models": {
        "sdr": str - speaker diarization recognition model,
        "scd": str - speaker change detection model,
        "asr": str - auto-speech recognition model,
        "vad": str - voice activity detection model,
        "punct": str - model for restoring punctuation and capital letters
    }
}
```
"""

import re
import json
from copy import deepcopy
from typing import Any, List, Union
from uuid import uuid4

try:
    from .rttm import str2list
except ImportError:
    pass

try:
    from .files import open_json, save_json
except ImportError:
    pass


def rttm2jsr(rttm: Union[List[List[str]], str]):
    """
    Convert rttm to JSR.

    Args
    ----------
        `rttm` : list or str rttm.

    Return
    ----------
        `JSR` : JSR file format.
    """
    if type(rttm) == str:
        rttm = str2list(rttm)
    return [
        {
            "speaker": {"idx": line[7], "conf": line[8]},
            "speech": {
                "time_start": float(line[3]),
                "time_end": float(line[3]) + float(line[4]),
                "duration": float(line[4]),
            },
        }
        for line in rttm
    ]


def combine_asr_sdr(
    jsr_asr: Union[List[dict], str],
    jsr_sdr: Union[List[dict], str],
    path_save: str = None,
):
    """
    Combine JSR ASR with JSR SDR.

    Args
    ----------
        `jsr_asr` : path to JSR ASR file or jsr asr variable

        `jsr_sdr` : path to JSR SDR file or jsr sdr variable

        `path_save` (opt): path to save combined JSR file

    Return
    ----------
        `JSR` : combined jsr
    """
    if type(jsr_asr) == str:
        jsr_asr = open_json(jsr_asr)

    if type(jsr_sdr) == str:
        jsr_sdr = open_json(jsr_sdr)

    temp_jsr_sdr = [(i, replica) for i, replica in enumerate(deepcopy(jsr_sdr))]

    for replica in jsr_asr:
        for token in replica["speech"]["tokens"]:
            middle_time = (token["end"] + token["start"]) / 2

            n = 0
            for i, temp_replica in [_ for _ in temp_jsr_sdr]:
                if (
                    middle_time > temp_replica["speech"]["time_start"]
                    and middle_time < temp_replica["speech"]["time_end"]
                ):
                    if "tokens" not in jsr_sdr[i]["speech"]:
                        jsr_sdr[i]["speech"]["tokens"] = [token]
                    else:
                        jsr_sdr[i]["speech"]["tokens"].append(token)
                    if "text" not in jsr_sdr[i]["speech"]:
                        jsr_sdr[i]["speech"]["text"] = token["word"]
                    else:
                        jsr_sdr[i]["speech"]["text"] += f" {token['word']}"
                    break
                elif token["end"] < temp_replica["speech"]["time_start"]:
                    break
                elif token["start"] > temp_replica["speech"]["time_end"]:
                    temp_jsr_sdr.pop(n)
                else:
                    n += 1

    if path_save:
        save_json(path_save, jsr_sdr)

    jsr_sdr = [
        row
        for row in jsr_sdr
        if "text" in row["speech"]
        and row["speech"]["text"]
        and row["speech"]["text"] != " "
        and row["speech"]["text"] != "  "
    ]

    return jsr_sdr


def add_speakers_names(jsr: List[dict], speaker_idx2name: dict):
    """
    Add speakers names to existing JSR.

    Args
    ----------
        `jsr` : JSR list  of dicts

        `speaker_idx2name` : dict of speakaer_idx:speaker_name format
    """
    for replica in jsr:
        idx = replica["speaker"]["idx"]
        if idx in speaker_idx2name:
            replica["speaker"]["display_name"] = speaker_idx2name[idx]
        else:
            replica["speaker"]["display_name"] = re.sub("_", " ", idx)


def dict2str(jsr: List[dict]):
    """
    Convert JSR dict to json str.

    Args
    ----------
        `jsr` : JSR dict

    Return
    ----------
        `str` : str in JSON format
    """
    return json.dumps(jsr)


def get_vad_jsr(jsr: List[dict]):
    return [
        {
            "speech": {
                "time_start": row["speech"]["time_start"],
                "time_end": row["speech"]["time_end"],
                "duration": row["speech"]["duration"],
            }
        }
        for row in jsr
    ]


def add_replicas_ids(jsr: List[dict]):
    return [{**replica, **{"id": str(uuid4())}} for replica in jsr]


def add_path_file_jsr(jsr: List[dict], path_file: str):
    return [{**replica, **{"path_file": path_file}} for replica in jsr]


def add_idx_file_jsr(jsr: List[dict], idx_file: str):
    return [{**replica, **{"idx_file": idx_file}} for replica in jsr]


def change_dict(d: dict, keys: List[str], value: Any):
    last_d = d
    for key in keys[:-1]:
        last_d = last_d[key]
    last_d[keys[-1]] = value
    return d


def add_last_time_end_jsr(jsr: List[dict], last_time_end: float):
    return [
        change_dict(
            change_dict(
                replica,
                ["speech", "time_start"],
                last_time_end + replica["speech"]["time_start"],
            ),
            ["speech", "time_end"],
            last_time_end + replica["speech"]["time_end"],
        )
        for replica in jsr
    ]


def change_all_time_jsr(jsr: List[dict], time_change: float):
    return [
        change_dict(
            change_dict(
                change_dict(
                    replica,
                    ["speech", "time_start"],
                    time_change + replica["speech"]["time_start"],
                ),
                ["speech", "time_end"],
                time_change + replica["speech"]["time_end"],
            ),
            ["speech", "tokens"],
            [
                change_dict(
                    change_dict(token, ["start"], token["start"] + time_change),
                    ["end"],
                    token["end"] + time_change,
                )
                for token in replica["speech"]["tokens"]
            ],
        )
        for replica in jsr
    ]


def convert_for_solr(jsr: List[dict], speech_idx: str):
    return [
        {
            "id": replica["id"],
            "text": replica["speech"]["text"],
            "time_start": replica["speech"]["time_start"],
            "speech_id": speech_idx,
            "speaker_id": replica["speaker"]["idx"],
        }
        for replica in jsr
    ]


def remove_keys_dict(d: dict, keys: List[str]):
    for key in keys:
        del d[key]
    return d


def remove_tokens_jsr(jsr: dict):
    return [
        {**replica, **{"speech": remove_keys_dict(replica["speech"], ["tokens"])}}
        for replica in jsr
    ]
