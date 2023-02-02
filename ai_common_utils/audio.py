"""
Audio utils for AI projects.
"""

import io
import wave
import logging
import datetime
import subprocess
from typing import Union

from .files import check_file


try:
    import numpy as np

    def int2float(sound: np.int16) -> np.float32:
        """
        Function for converting audio np.int16 to np.float32.

        Parameters
        ----------
        sound: np.int16
            Sound sample in np.int16 format.

        Returns
        -------
        sound: np.float32
            Sound sample in np.float32 format.
        """
        abs_max = np.abs(sound).max()
        sound = sound.astype("float32")
        if abs_max > 0:
            sound *= 1 / abs_max
        sound = sound.squeeze()
        return sound

except ImportError:
    logging.error("Numpy not installed. audio.int2float not allowed!")


try:
    from pydub import AudioSegment

    def get_audio_segment(audio_file: AudioSegment, time_from: float, time_to: float):
        """
        Function for getting segment from AudioSegment with setted start time and end time in seconds.

        Parameters
        ----------
        audio_file: AudioSegment
            Segment of audio.
        time_from: float
            Float time from which start in seconds.
        time_to: float
            Float time when interval ended in seconds.

        Returns
        -------
        segment: io.BytesIO
            Audio segment.
        """
        """"""
        time_from = time_from * 1000  # Works in milliseconds
        time_to = time_to * 1000
        audio_seg = audio_file[time_from:time_to]
        temp_f = io.BytesIO()
        audio_seg.export(temp_f, format="wav")
        return temp_f

except ImportError:
    logging.error("pydub not installed. audio.get_audio_segment not allowed!")


def get_audio_seg(
    wave_file: wave.Wave_read, t_start: float, t_time: float, wav_file_info: dict
):
    """
    Function for cutting from wave opened file with setted start time and time interval in seconds.

    Parameters
    ----------
    wave_file: wave.Wave_read
        Opened to read wave file.
    t_start: float
        Float time from which start in seconds.
    t_time: float
        Float time interval in seconds.
    wav_file_info: dict
        Dict with appropriate wave file info.

        (CHANNELS, SAMP_WIDTH, RATE)

    Returns
    -------
    frames: bytes
        wave frames bytes for appropriate time interval.
    """
    """"""
    wave_file.setpos(int(wav_file_info["RATE"] * t_start))
    return wave_file.readframes(int(wav_file_info["RATE"] * t_time))


def file2bytes(path_audio: str):
    """
    Read audio file from path as bytes.

    Parameters
    ----------
    path_audio: str
        Path to audio file.

    Returns
    -------
    file: io.BytesIO
        Bytes tempalte file of audio file.
    """
    temp_file = None
    with open(path_audio, "rb") as f:
        temp_file = io.BytesIO(f.read())  # b64encode
    return temp_file


def cut_audio_bytes(data: bytes, time_start: float = None, time_end: float = None):
    if time_start and not time_end:
        data = data[int(time_start * 16000) :]

    elif time_end and not time_start:
        data = data[: int(time_end * 16000 - 1)]

    elif time_start and time_end:
        data = data[int(time_start * 16000) : int(time_end * 16000 - 1)]

    return data


def get_hms(seconds: float):
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return "{:02.0f}:{:02.0f}:{:02.0f}".format(hours, minutes, seconds)


def get_audio(
    data: Union[str, io.BytesIO, bytes],
    time_start: float = None,
    time_end: float = None,
):
    """
    Universal function for get audio from different types of data (path, obj, video).

    Parameters
    ----------
    data: Union[str, io.BytesIO, bytes]
        Path to audio file, obj file or video.

    Returns
    -------
    audio: io.BytesIO
        Bytes tempalte file of audio.
    """

    if type(data) == str:
        cmd = ["ffmpeg"]

        if time_start:
            cmd.extend(["-ss", get_hms(time_start)])

            if time_end and time_end > time_start:
                cmd.extend(["-t", get_hms(time_end - time_start)])

        cmd.extend(
            [
                "-i",
                data,
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                "pipe:.wav",
                "-hide_banner",
                "-loglevel",
                "error",
            ]
        )

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        out = proc.communicate()[0]

        proc.wait()

        return io.BytesIO(out)

    elif type(data) == io.BytesIO or type(data) == bytes:
        if type(data) == io.BytesIO:
            data = data.getvalue()

        cmd = ["ffmpeg"]

        if time_start:
            cmd.extend(["-ss", get_hms(time_start)])

            if time_end and time_end > time_start:
                cmd.extend(["-t", get_hms(time_end - time_start)])
        cmd.extend(
            [
                "-i",
                "-",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                "pipe:.wav",
                "-hide_banner",
                "-loglevel",
                "error",
            ]
        )

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            bufsize=len(data),
            shell=False,
        )
        out = proc.communicate(input=data, timeout=None)[0]

        proc.wait()

        return io.BytesIO(out)

    else:
        raise TypeError(
            "Unsupported type of input! Put in func str path to file or io.BytesIO."
        )


def get_time_audio(audio: io.BytesIO, return_str: bool = True):
    """
    Get time of audio from temp file bytes.

    Parameters
    ----------
    audio: io.BytesIO
        Temp audio file.
    return_str: bool
        True - Return str time.

        False - return datetime.timedelta.

    Returns
    -------
    time: str
        Time in H:M:S ISO-8601 format.
    """
    audio = check_file(audio)
    wf = wave.open(audio, "rb")

    nframes = wf.getnframes()

    # Found bag with always return this value:
    if nframes == 2147483647:
        nframes = len(wf.readframes(nframes)) / 2

    framerate = wf.getframerate()

    if return_str:
        return str(datetime.timedelta(seconds=int(nframes / framerate)))
    else:
        return datetime.timedelta(seconds=int(nframes / framerate))
