from dataclasses import dataclass
from collections.abc import Sequence, Iterable, Callable, Mapping
from functools import wraps
from typing import Any

from larch.symboltable import Group

@dataclass(frozen=True)
class Operation:
    """A discrete computational unit of analysis."""

    desc: str
    func: Callable[[Sequence[Group], ...], Sequence[Group]]
    args: tuple[Any, ...]
    kwargs: Mapping[Any, Any]


def operation(desc: str):
    """A decorator that"""

    def wrapper(fn: Callable[[Sequence[Group], ...], Sequence[Group]]):
        @wraps(fn)
        def inner(analysis: "BaseAnalysis", *args, **kwargs) -> "BaseAnalysis":
            new_operation = Operation(desc=desc, func=fn, args=args, kwargs=kwargs)
            new_analysis = type(analysis)(
                groups=analysis.groups,
                operations=(*analysis.operations, new_operation),
                past_operations=analysis.past_operations,
            )
            return new_analysis

        return inner

    return wrapper


class BaseAnalysis:
    groups: Sequence[Group]
    operations: tuple[Operation, ...]

    def __init__(
        self,
        groups: Iterable[Group] = (),
        operations: tuple[Operation, ...] = (),
        past_operations: tuple[Operation, ...] = (),
    ):
        self.groups = groups
        self.operations = operations
        self.past_operations = past_operations
