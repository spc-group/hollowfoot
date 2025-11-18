from collections.abc import Sequence

from larch.symboltable import Group as LarchGroup  # noqa: F401

__all__ = ["Group"]


class Group(LarchGroup):
    past_operations: Sequence

    def __init__(self, *args, **kwargs):
        self.past_operations = ()
        super().__init__(*args, **kwargs)
