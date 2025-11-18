import warnings
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Protocol

from .group import Group
from .readers import read_aps_20bmb


class OperatorFunction(Protocol):
    def __call__(self, groups: Sequence[Group], *args, **kwargs) -> list[Group]: ...


@dataclass(frozen=True)
class Operation:
    """A discrete computational unit of analysis."""

    desc: str
    func: OperatorFunction
    args: tuple[Any, ...]
    kwargs: Mapping[Any, Any]


def operation(desc: str):
    """A decorator that"""

    def wrapper(fn: OperatorFunction):
        @wraps(fn)
        def inner(analysis: "Analysis", *args, **kwargs) -> "Analysis":
            new_operation = Operation(desc=desc, func=fn, args=args, kwargs=kwargs)
            new_analysis = type(analysis)(
                groups=analysis.groups,
                operations=(*analysis.operations, new_operation),
            )
            return new_analysis

        return inner

    return wrapper


class Analysis:
    groups: Iterable[Group]
    operations: tuple[Operation, ...]

    def __init__(
        self,
        groups: Iterable[Group] = (),
        operations: tuple[Operation, ...] = (),
    ):
        self.groups = groups
        self.operations = operations

    def calculate(self):
        """Apply all pending operations and produce a new analysis object."""
        groups = self.groups
        operations = self.operations
        for op in self.operations:
            groups = op.func(list(groups), *op.args, **op.kwargs)
        groups = tuple(groups)
        # Keep track of the operations that have already been performed on the groups
        for group in groups:
            group.past_operations = (
                *getattr(group, "past_operations", ()),
                *operations,
            )
        if len(groups) == 0:
            warnings.warn(f"Operation {op} produced 0 valid groups")
        return type(self)(
            tuple(groups),
            operations=[],
        )

    @classmethod
    def from_aps_20bmb(
        cls, base: str | Path, glob: str = "", regex: str = ""
    ) -> "Analysis":
        """Read XAFS data measured at APS beamline 20-BM-B.

        The first argument can be either a specific file to read, or a
        directory containing such files.

        Selecting specific files from a directory can be accomplished
        using either globs or regular expressions:

        .. code-block:: python

            read_aps_20bmb_

        Parameters
        ==========
        base
          A filesystem path in which to look for files, or else a
          specific file to read.
        reader
          The function that knows how to load data in this specific format.
        glob
          If *base* is a directory, this glob will be used as a pattern
          for restricting files.
        regex
          If *base* is a directory, only files matching this regular
          expression will be read.

        """
        groups = read_aps_20bmb(base=base, glob=glob, regex=regex)
        return cls(groups=groups)
