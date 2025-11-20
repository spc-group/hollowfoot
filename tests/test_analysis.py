from inspect import BoundArguments
from pathlib import Path

import numpy as np
import pytest

from hollowfoot import Analysis, Group, operation

data_dir = Path(__file__).parent / "data"


class TestAnalysis(Analysis):
    @operation(desc="run test code later")
    def noop(groups, color="red"):
        return groups

    @operation(desc="run test code now", defer=False)
    def now_task(groups, orientation="vertical"):
        for group in groups:
            group.orientation = orientation
        print(groups)
        return groups


@pytest.fixture()
def analysis():
    group = Group(x=np.linspace(0, 100, num=19))
    anl = TestAnalysis((group,))
    return anl


def test_analysis_chaining(analysis):
    new_anl = analysis.noop()
    assert isinstance(new_anl, Analysis)
    assert new_anl is not analysis


def test_operation_adds_to_stack():
    anl = TestAnalysis().noop()
    assert len(anl.operations) == 1
    assert anl.operations[0].desc == "run test code later"


def test_operation_call_immediately():
    """Does the `defer=False` flag cause the operation to happen
    immediately?

    """
    anl = TestAnalysis(groups=(Group(),)).now_task(orientation="diagonal")
    assert len(anl.operations) == 0
    group = anl.groups[0]
    assert len(group.past_operations) == 1
    assert group.orientation == "diagonal"


def test_operation_binds_arguments():
    """Check that an operation includes bound arguments in it's attributes."""
    anl = TestAnalysis(groups=(Group(),)).noop().calculate()
    (group,) = anl.groups
    (op,) = group.past_operations
    assert isinstance(op.bound_arguments, BoundArguments)


def test_read_aps_20bmb(tmp_path):
    data_file = data_dir / "Ni-foil-EXAFS.0002"
    analysis = Analysis.from_aps_20bmb(data_file)
    assert len(analysis.groups) == 1


def test_past_operations(analysis):
    analysis = analysis.noop()
    assert len(analysis.groups[0].past_operations) == 0
    analysis = analysis.calculate()
    assert len(analysis.groups[0].past_operations) == 1
    # Do another one
    analysis = analysis.noop().calculate()
    assert len(analysis.groups[0].past_operations) == 2


def test_past_operations_chain(analysis):
    """Do the past operations get tracked properly for every step."""

    class ChainAnalysis(Analysis):
        @operation("record past number of operations")
        def track_num_ops(groups):
            for group in groups:
                group["past_op_count"] = len(group.past_operations)
            return groups

    anl = ChainAnalysis(groups=(Group(),))
    anl = anl.track_num_ops().track_num_ops()
    assert getattr(anl.groups[0], "past_op_count", 0) == 0
    anl = anl.calculate()
    assert getattr(anl.groups[0], "past_op_count", 0) == 1
