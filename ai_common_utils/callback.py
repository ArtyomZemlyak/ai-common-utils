"""
Callbacks utils.
"""

import datetime
from time import time
from typing import Any, List, Union


class ProgressCallback:
    """
    Estimate progress of process through callbacks and execute provided function.

    Args
    ----------
        `target_state`: value of target state of process.

        `init_state` (opt=0): value of initial state of process.

        `func_exec` (opt): function that will be executed with current state argument, if method `call` is called.

        `callback_interval` (opt=5): interval in seconds between execution `func_exec`.
    """

    def __init__(
        self,
        target_state: Union[int, float],
        init_state: Union[int, float] = 0,
        func_exec=None,
        callback_interval: Union[int, float] = 5,
        coeff: Union[int, float] = 1,
        block_coeff: bool = False,
    ) -> None:
        self.target_state = target_state
        self.state = init_state
        self.func_exec = func_exec
        self.callback_interval = callback_interval
        self.last_callback = 0
        self.coeff = coeff
        self.block_coeff = block_coeff

    def __call__(self, step: Union[int, float], *args: Any, **kwds: Any) -> Any:
        if not self.block_coeff:
            step = step * self.coeff

        self.state += step

        if self.func_exec and time() - self.last_callback > self.callback_interval:
            self.func_exec(self.state / self.target_state)
            self.last_callback = time()

    def call(self, step: Union[int, float]):
        self.__call__(step)

    def set_coeff(self, coeff: Union[int, float]):
        self.coeff = coeff


class TimerCallback:
    """
    Estimate time of process through callbacks and execute provided function.

    Args
    ----------
        `target_state`: value of target state of process.

        `start_time` (opt): time from which timer starts.

        `end_time` (opt=datetime.timedelta(seconds=0)): time when timer stops.

        `func_exec` (opt): function that will be executed with current timer argument, if method `call` is called.

        `callback_interval` (opt=5): interval in seconds between execution `func_exec`.
    """

    def __init__(
        self,
        target_state: Union[int, float],
        start_time: datetime.timedelta,
        end_time: datetime.timedelta = datetime.timedelta(seconds=0),
        func_exec=None,
        callback_interval: Union[int, float] = 5,
        coeff: Union[int, float] = 1,
        block_coeff: bool = False,
    ) -> None:
        self.target_state = target_state
        self.all_time = start_time - end_time
        self.timer = start_time
        self.func_exec = func_exec
        self.callback_interval = callback_interval
        self.last_callback = 0
        self.coeff = coeff
        self.block_coeff = block_coeff

    def __call__(
        self, step: Union[float, datetime.timedelta], *args: Any, **kwds: Any
    ) -> Any:
        if not self.block_coeff:
            step = step * self.coeff

        if type(step) == float or type(step) == int:
            step = step / self.target_state
            if step > 0 and step <= 1:
                step = self.all_time * step
            else:
                raise ValueError(
                    f"step only > 0 and <= target_state={self.target_state}"
                )

        if step < self.timer:
            self.timer -= step
        else:
            self.timer = datetime.timedelta(seconds=0)

        if self.func_exec and time() - self.last_callback > self.callback_interval:
            self.func_exec(str(self.timer))
            self.last_callback = time()

    def call(self, step: Union[float, datetime.timedelta]):
        """
        step only > 0 and <= 1
        """
        self.__call__(step)

    def set_coeff(self, coeff: Union[int, float]):
        self.coeff = coeff


class StopwatchCallback:
    """
    Estimate spended time of process through callbacks and execute provided function.

    Args
    ----------
        `start_time` (opt): time from which stopwatch starts.

        `func_exec` (opt): function that will be executed with current timer argument, if method `call` is called.

        `callback_interval` (opt=5): interval in seconds between execution `func_exec`.
    """

    def __init__(
        self,
        start_time: datetime.datetime,
        func_exec=None,
        callback_interval: Union[int, float] = 5,
    ) -> None:
        self.start_time = start_time
        self.time_now = datetime.datetime.now() - start_time
        self.func_exec = func_exec
        self.callback_interval = callback_interval
        self.last_callback = 0

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.time_now = datetime.datetime.now() - self.start_time

        if self.func_exec and time() - self.last_callback > self.callback_interval:
            self.func_exec(str(self.time_now))
            self.last_callback = time()

    def call(self, step=None):
        """
        No step! Just call.
        """
        self.__call__()

    def set_coeff(self, coeff):
        pass


def call_callbacks(val: Union[int, float], callbacks: List[ProgressCallback]):
    if callbacks:
        _ = [_callback.call(val) for _callback in callbacks]


def callbacks_set_coeff(coeff: Union[int, float], callbacks: List[ProgressCallback]):
    if callbacks:
        _ = [_callback.set_coeff(coeff) for _callback in callbacks]
