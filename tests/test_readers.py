from pathlib import Path

from hollowfoot.readers import read_aps_20bmb, resolve_file_paths

data_dir = Path(__file__).parent / "data"


def test_resolve_single_file(tmp_path):
    # Set up some files to check
    good_path = tmp_path / "spam.eggs"
    good_path.touch()
    resolved = resolve_file_paths(good_path)
    assert resolved == [good_path]


def test_resolve_directory(tmp_path):
    # Set up some files to check
    good_path = tmp_path / "spam.eggs"
    good_path.touch()
    bad_path = tmp_path / "spam.parrot"
    bad_path.touch()
    resolved = resolve_file_paths(tmp_path)
    assert set(resolved) == {good_path, bad_path}


def test_resolve_file_globs(tmp_path):
    # Set up some files to check
    good_path = tmp_path / "spam.eggs"
    good_path.touch()
    bad_path = tmp_path / "spam.parrot"
    bad_path.touch()
    resolved = resolve_file_paths(tmp_path, glob="s*s")
    assert resolved == [good_path]


def test_resolve_file_regex(tmp_path):
    # Set up some files to check
    good_path = tmp_path / "spam.eggs"
    good_path.touch()
    bad_path = tmp_path / "spamparrot"
    bad_path.touch()
    resolved = resolve_file_paths(tmp_path, regex=r"spam\..+")
    assert resolved == [good_path]


def test_read_aps_20bmb(tmp_path):
    data_file = data_dir / "Ni-foil-EXAFS.0002"
    groups = read_aps_20bmb(data_file)
    assert len(groups) == 1
