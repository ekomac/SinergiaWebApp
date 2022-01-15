from typing import Any, Callable


def call_or_it(may_be_called: Any or Callable, value):
    if callable(may_be_called):
        return may_be_called(value)
    return may_be_called
