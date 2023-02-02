"""
Doc utils.
"""

from typing import Callable


def copy_doc(copy_func: Callable) -> Callable:
    """Use Example: copy_doc(self.copy_func)(self.func) or used as deco"""

    def wrapper(func: Callable) -> Callable:
        # if func.__doc__:
        #     func.__doc__ += str(copy_func.__doc__)
        # else:
        #     func.__doc__ = copy_func.__doc__
        func.__doc__ = copy_func.__doc__
        return func

    return wrapper
