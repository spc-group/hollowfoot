import re
from pathlib import Path
from collections.abc import Sequence, Callable

from larch.symboltable import Group
from larch.io import read_ascii


def resolve_file_paths(base: Path, glob: str = "", regex: str = "") -> list[Path]:
    """Figures out which files in a *base* path match the glob and
    regex provided.

    Also, *base* can be a path to a file, then just the base path is
    returned.

    """
    if base.is_file():
        return [base]
    # Apply glob matching
    if glob:
        children = list(base.glob(glob))
    else:
        children = list(base.iterdir())
    # Apply regex
    regex_ = re.compile(regex)
    children = [path for path in children if regex_.search(str(path))]
    return children


class NotADataFile:
    """Sentinel for if a specific file should be skipped because it has no data."""
    pass


def read_text_files(
        paths: Sequence[Path], reader: Callable[[Path, ...], Group], glob: str = "", regex="",
) -> Sequence[Group]:
    """Iterate data groups from text files.

    Useful for making beamline-specific input functions.

    Parameters
    ==========
    base
      Path objects that will be opened and read for data.
    reader
      The function that knows how to load data in this specific format.

    """
    for path in paths:
        maybe_group = reader(path)
        if isinstance(maybe_group, NotADataFile):
            continue
        yield maybe_group


def read_aps_20bmb(base: str | Path, glob: str = "", regex: str = "") -> list[Group]:
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
    paths = resolve_file_paths(Path(base), glob=glob, regex=regex)
    
    def reader(fp):
        if fp.suffix == ".last":
            return NotADataFile()
        return read_ascii(fp)

    groups = list(read_text_files(paths, reader))
    return groups
