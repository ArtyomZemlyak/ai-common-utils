"""
Date and time utils.
"""

import datetime


def format_time(dt_time: datetime.timedelta):
    """
    Format time in H:M:S format.

    Args
    ----------
        `dt_time` : datetime.timedelta.

    Return
    ----------
        `str` : time in H:M:S format.
    """
    str_time = str(dt_time)
    str_time = str_time.split(", ")[-1]
    h, m, s = str_time.split(":")

    if len(h) == 1:
        h = "0" + h

    if "." in s or "," in s:
        s = s[:-3]

    return f"{h}:{m}:{s}"
