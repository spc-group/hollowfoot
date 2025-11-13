import pytest

from larch.symboltable import Group
import numpy as np

from hollowfoot import XAFSAnalysis, operation


@pytest.fixture()
def group():
    grp = Group(
        mono_energy=np.linspace(8320, 8350, num=1),
        It=np.sin(np.pi*4) + 1.5,
        I0=np.cos(np.pi*6) + 1.5,
    )
    return grp


def test_to_mu(group):
    anl = (
        XAFSAnalysis(groups=(group,))
        .to_mu("mono_energy", "It", "I0", is_transmission=True)
        .calculate()
    )
    assert anl.groups[0].mu == np.log(group.I0/group.It)

def test_to_mu_missing_keys(group):
    # What if none of the groups have the requested key
    anl = (
        XAFSAnalysis(groups=(group,))
        .to_mu("mono_energy", "Inull", "I0", is_transmission=True)
    )
    with pytest.raises(AttributeError):
        anl.calculate()
