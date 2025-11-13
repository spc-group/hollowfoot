from ._version import get_versions
from .analysis import Analysis, operation  # noqa: F401
from .xafs_analysis import XAFSAnalysis  # noqa: F401


__version__ = get_versions()["version"]
del get_versions

# TODO: fill this in with appropriate star imports:
__all__ = ["Analysis", "operation"]
