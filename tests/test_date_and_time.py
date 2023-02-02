from os import path
import datetime
import sys

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from ai_common_utils.date_and_time import format_time


def test_format_time():
    t1 = datetime.datetime.fromisoformat("2022-07-16T14:25:56+00:00")
    t2 = datetime.datetime.fromisoformat("2023-11-13T11:36:15+00:00")
    dt = t2 - t1

    assert format_time(dt) == "21:10:19"
