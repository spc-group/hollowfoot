from pathlib import Path
from collections.abc import Sequence, Callable

from larch.symboltable import Group
from larch.io import read_ascii

from hollowfoot.analysis import Analysis


class NotADataFile:
    """Sentinel for if a specific file should be skipped because it has no data."""
    pass


def read_text_files(
    base: Path, reader: Callable[[Path, ...], Group]
) -> Sequence[Group]:
    if base.is_file():
        yield reader(base)
    # We have a folder or file path stub, look for matching files
    base_dir = base if base.is_dir() else base.parent
    target_name = str(base.relative_to(base_dir))
    matching_files = [
        fp for fp in base_dir.iterdir() if fp.name.startswith(target_name)
    ]
    for fp in matching_files:
        maybe_group = reader(fp)
        if isinstance(maybe_group, NotADataFile):
            continue
        yield maybe_group


def from_aps_20bmb(base: str | Path):
    def reader(fp):
        if fp.suffix == ".last":
            return NotADataFile()
        return read_ascii(fp)

    groups = list(read_text_files(Path(base), reader))
    return Analysis(groups)
