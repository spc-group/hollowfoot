from pathlib import Path

import numpy as np
import pytest

from hollowfoot import Analysis, Group, operation

data_dir = Path(__file__).parent / "data"


class TestAnalysis(Analysis):
    @operation(desc="run test code")
    def noop(groups, color="red"):
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
    assert anl.operations[0].desc == "run test code"


# def test_operation_binds_arguments():
#     """Check that an operation includes bound arguments in it's attributes."""
#     anl = TestAnalysis().noop()
#     (op,) = anl.operations
#     assert isinstance(op.bound_arguments, BoundArguments)


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
