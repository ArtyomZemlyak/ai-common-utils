"""
Rttm utils for Varvara project.

RTTM file specification:
Field 1 2       3       4       5       6       7       8       9       10
Type    file    chnl    tbeg    tdur    ortho   stype   name    conf    Slat
https://web.archive.org/web/20170119114252/http://www.itl.nist.gov/iad/mig/tests/rt/2009/docs/rt09-meeting-eval-plan-v2.pdf
p 12
"""

from typing import List, Union

try:
    from .files import open_list_rttm, open_json, save_list_rttm
except ImportError:
    pass


def str2list(rttm: str):
    """
    Convert str rttm to list rttm.

    Args
    ----------
        `rttm` : str rttm.

    Return
    ----------
        `List[List[str]]` : list rttm.
    """
    return [
        line.split(" ")
        for line in rttm.split("\n")
        if line != "" and line != " " and line != "\n"
    ]


def list2str(rttm: List[List[str]]):
    """
    Convert list rttm to str rttm.

    Args
    ----------
        `rttm` : list rttm.

    Return
    ----------
        `str` : str rttm.
    """
    return "\n".join([" ".join(line) for line in rttm])


def get_timestamps(rttm: List[List[str]], do_enumerate: bool = True):
    """
    Convert list rttm with str values to list rttm with only float values (specific columns converted from str to float).

    Args
    ----------
        `rttm` : list rttm.

        `enumerate` (opt): add enumerate columnt in first pos.

    Return
    ----------
        `List[Tuple[int, float, float]]` : truncated float rttm with additional enumerate column, start time and time of speech interval.
        `List[Tuple[float, float]]` :  truncated float rttm with start time and time of speech interval.
    """
    if do_enumerate:
        return [
            (i, float(t_start), float(t_time))
            for i, (_, _, _, t_start, t_time, _, _, _, _, _) in enumerate(rttm)
        ]
    else:
        return [
            (float(t_start), float(t_time))
            for _, _, _, t_start, t_time, _, _, _, _, _ in rttm
        ]


def get_ts_and_names(rttm: List[List[str]], do_enumerate: bool = True):
    """
    Convert list rttm with str values to list rttm with only float values and speaker name (specific columns converted from str to float).

    Args
    ----------
        `rttm` : list rttm.

        `enumerate` (opt): add enumerate columnt in first pos.

    Return
    ----------
        `List[Tuple[int, float, float, name]]` : truncated float rttm with additional enumerate column, start and end time of speech interval, name of speaker.
        `List[Tuple[float, float, name]]` :  truncated float rttm with start and end time of speech interval, name of speaker.
    """
    if do_enumerate:
        return [
            (i, float(t_start), float(t_start) + float(t_time), name)
            for i, (_, _, _, t_start, t_time, _, _, name, _, _) in enumerate(rttm)
        ]
    else:
        return [
            (float(t_start), float(t_start) + float(t_time), name)
            for _, _, _, t_start, t_time, _, _, name, _, _ in rttm
        ]


def combine_rttm_and_text_vosk(
    rttm: Union[str, List[List[str]]],
    text_vosk: Union[str, List[dict]],
    path_combined_rttm: str = None,
):
    """
    Combine rttm and text recognized with vosk.

    Args
    ----------
        `rttm` : path to rttm file or list rttm.

        `text_vosk` : path to text vosk json file or List[dict] with vosk recognized text.

        `path_combined_rttm` (opt): path to save combined rttm.

    Return
    ----------
        `List[List[str]]` : list rttm with additional text words in idx=7 column.
    """
    if type(rttm) == str:
        rttm = open_list_rttm(rttm)

    temp_rttm = get_ts_and_names(rttm)

    if type(text_vosk) == str:
        text_rec = open_json(text_vosk)
    elif type(text_vosk) == list:
        text_rec = text_vosk
    else:
        raise TypeError(
            "Recognized text from vosk can be only List[dict] type, or str path to json file."
        )

    for text_line in text_rec:
        if "result" in text_line:
            for text_item in text_line["result"]:
                middle_time = (text_item["end"] + text_item["start"]) / 2
                word = text_item["word"]

                n = 0
                for i, t_start, t_end, name in [_ for _ in temp_rttm]:
                    if middle_time > t_start and middle_time < t_end:
                        rttm[i][7] += f"/{word}"
                        break
                    elif text_item["end"] < t_start:
                        break
                    elif text_item["start"] > t_end:
                        temp_rttm.pop(n)
                    else:
                        n += 1

    if path_combined_rttm:
        save_list_rttm(path_combined_rttm, str2list(rttm))

    return rttm


def jsr2rttm(jsr: dict):
    return [
        [
            "SPEAKER",
            "<NA>",
            "1",
            f'{row["speech"]["time_start"]}',
            f'{row["speech"]["duration"]}',
            "<NA>",
            "<NA>",
            f'{row["speaker"]["idx"]}{"/".join(row["speech"]["text"].split(" ")) if "text" in row["speech"] else ""}'
            if "speaker" in row
            else "<NA>",
            f'{row["speaker"]["conf"]}'
            if "speaker" in row and "conf" in row["speaker"]
            else "<NA>",
            "<NA>",
        ]
        for row in jsr
    ]
