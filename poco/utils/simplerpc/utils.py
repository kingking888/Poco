# coding=utf-8
from functools import wraps


def sync_wrapper(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        cb = func(*args, **kwargs)
        ret, err = cb.wait(timeout=5)
        if err:
            raise err
        return ret
    return new_func