import warnings
from collections.abc import Callable, Iterable, Sequence
from copy import copy
from functools import wraps
from pathlib import Path
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import wraps
from typing import Any

import numpy as np
from larch.io import merge_groups, read_ascii
from larch.plot import bokeh_xafsplots as xafsplots
from larch.symboltable import Group
from larch.xafs import pre_edge
from larch.symboltable import Group

from hollowfoot.base_analysis import BaseAnalysis, operation




# BAD_CHARS = ",#@%|:* "


# def clean_group_name(value: str):
#     for bchar in BAD_CHARS:
#         value = value.replace(bchar, "_").lower()
#     return value


class Analysis(BaseAnalysis):
    def is_flattened(self):
        print([op.func for op in self.past_operations])
        return self.fit_edge_jump.__wrapped__ in [
            op.func for op in self.past_operations
        ]

    @operation(desc="Calculate µ(E)")
    def to_mu(
        groups: Sequence[Group],
        energy: str,
        signal: str,
        reference: str | None = None,
        is_transmission=False,
    ):
        for group in groups:
            try:
                ydata = getattr(group, signal)
                rdata = getattr(group, reference) if reference is not None else 1
            except AttributeError as exc:
                # Incomplete scan, so skip it
                warnings.warn(
                    f"Could not read column: {exc} from {group}. Removing this scan from analysis."
                )
                continue
            mu = ydata / rdata
            if is_transmission:
                mu = -np.log(mu)
            yield Group(mu=mu, energy=getattr(group, energy))

    def calculate(self):
        """Apply all pending operations and produce a new analysis object."""
        groups = self.groups
        operations = self.operations
        for op in self.operations:
            groups = op.func(list(groups), *op.args, **op.kwargs)

        return Analysis(
            tuple(groups),
            operations=[],
            past_operations=(*self.past_operations, *operations),
        )

    def summarize(self):
        new_analysis = self.calculate()
        print("Steps:")
        for operation in new_analysis.past_operations:
            print(f"- {operation.desc}")
        return new_analysis

    @operation(desc="merge data groups")
    def merge(groups, *args, **kwargs):
        return [merge_groups(groups, *args, **kwargs)]

    @wraps(xafsplots.plot_mu)
    def plot_mu(self, **kwargs):
        new_analysis = self.calculate()
        if "fig" in kwargs:
            fig = kwargs["fig"]
        else:
            fig = kwargs["fig"] = xafsplots.BokehFigure()
        # Get some default arguments
        kwargs.setdefault("show_flat", new_analysis.is_flattened())
        # Do the actual plotting
        for group in new_analysis.groups:
            fig = xafsplots.plot_mu(group, show=False, **kwargs)
        fig.show(show=True)
        return new_analysis

    @wraps(xafsplots.plot_chik)
    def plot_chik(self, **kwargs):
        new_analysis = self.calculate()
        if "fig" in kwargs:
            fig = kwargs["fig"]
        else:
            fig = kwargs["fig"] = xafsplots.BokehFigure()
        # Do the actual plotting
        for group in new_analysis.groups:
            fig = xafsplots.plot_chik(group, show=False, **kwargs)
        fig.show(show=True)
        return new_analysis

    @operation(desc="fit edge jump in µ(E)")
    def fit_edge_jump(groups, *args, **kwargs):
        for group in groups:
            new_group = copy(group)
            pre_edge(new_group, *args, **kwargs)
            yield new_group

