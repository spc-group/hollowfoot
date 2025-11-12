from larch.symboltable import Group
import numpy as np

from hollowfoot import Analysis, operation


class TestAnalysis(Analysis):
    @operation(desc="run test code")
    def noop(self, color="red"):
        pass



def test_analysis_chaining():
    group = Group(x=np.linspace(0, 100, num=19))
    anl = TestAnalysis((group,))
    new_anl = anl.noop()
    assert isinstance(new_anl, Analysis)
    assert new_anl is not anl


def test_operation_adds_to_stack():

    anl = TestAnalysis().noop()
    assert len(anl.operations) == 1
    assert anl.operations[0].desc == "run test code"
