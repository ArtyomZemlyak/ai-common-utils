"""
SRT (subtitles) utils.
"""

import datetime
import re
from typing import List, Union

from .files import open_list_rttm, open_json
from .rttm import get_ts_and_names
from .date_and_time import format_time


def rttm2srt(
    rttm: Union[str, List[List[str]]],
    path_srt: str = None,
    punct=None,
    speaker_idx2name: dict = None,
):
    """
    Convert rttm to SRT (subtitles).
    Args
    ----------
        `rttm` : path to rttm file or list rttm.

        `path_srt` (opt): path to SRT file to save.

        `punct` (opt): punctuation model CasePuncPredictor.

        `speaker_idx2name` (opt): dict of speakaer_idx:speaker_name format. If provided change idx to name for each speaker

    Return
    ----------
        `str` : SRT (subtitles)
    """
    if type(rttm) == str:
        rttm = open_list_rttm(rttm)

    rttm = get_ts_and_names(rttm, do_enumerate=False)

    srt = ""
    counter = 0

    for t_start, t_end, str_text in rttm:
        counter += 1
        srt += f"{counter}\n"
        srt += f"{format_time(datetime.timedelta(seconds=t_start))} --> {format_time(datetime.timedelta(seconds=t_end))}\n"

        if not punct:
            srt += f"{str_text}\n\n"
        else:
            str_text = str_text.split("/")

            name = str_text[0]

            if speaker_idx2name:
                if name in speaker_idx2name:
                    name = speaker_idx2name[name]

            name = re.sub("_", " ", name)

            str_text = str_text[1:]
            str_text.append(",")
            tokens = list(enumerate(str_text))
            results = ""

            for token, case_label, punc_label in punct.predict(tokens, lambda x: x[1]):
                prediction = punct.map_punc_label(
                    punct.map_case_label(token[1], case_label), punc_label
                )
                if token[1][0] != "#":
                    results = results + " " + prediction
                else:
                    results = results + prediction

            srt += f"{name}: {results[:-1]}\n\n"

    if path_srt:
        with open(path_srt, "w") as f:
            f.write(srt)

    return srt


def jsr2srt(jsr: Union[str, List[dict]], path_save: str = None):
    """
    Convert JSR to SRT (subtitles).
    Args
    ----------
        `rttm` : path to JSR file or jsr variable.

        `path_save` (opt): path to SRT file to save.

    Return
    ----------
        `str` : SRT (subtitles)
    """
    if type(jsr) == str:
        jsr = open_json(jsr)

    srt = ""
    counter = 0

    for replica in jsr:
        counter += 1
        name = (
            ""
            if "speaker" not in replica
            else replica["speaker"]["display_name"]
            if "display_name" in replica["speaker"]
            else replica["speaker"]["idx"]
        )
        name = f"{name}: " if name else name
        srt += f"{counter}\n"
        srt += f"{format_time(datetime.timedelta(seconds=replica['speech']['time_start']))} --> {format_time(datetime.timedelta(seconds=replica['speech']['time_end']))}\n"
        srt += f"{name}{replica['speech']['text']}\n\n"

    if path_save:
        with open(path_save, "w") as f:
            f.write(srt)

    return srt
