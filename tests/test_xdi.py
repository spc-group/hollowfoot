from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from hollowfoot.xdi import (
    Role,
    Token,
    XDIBackendEntrypoint,
    load,
    parse,
    tokenize,
    version_pattern,
)

xdi_path = Path(__file__).parent / "example.xdi"


def test_tokenizer():
    with open(xdi_path, mode="r") as fp:
        tokens = list(tokenize(fp.read()))

    assert tokens[0].role == Role.VERSION
    assert tokens[0].value == "XDI/1.0"
    assert tokens[1].role == Role.VERSION
    assert tokens[1].value == "GSE/1.0"
    assert tokens[2].role == Role.HEADER_NAME
    assert tokens[2].value == "Column.1"
    assert tokens[46].role == Role.USER_COMMENT
    assert tokens[46].value == "Cu foil Room Temperature"
    expected_columns = ["energy", "i0", "itrans", "mutrans"]
    column_labels = tokens[48:52]
    assert [col.role for col in column_labels] == [Role.COLUMN_LABEL] * len(
        expected_columns
    )
    assert [col.value for col in column_labels] == expected_columns
    assert tokens[52].role == Role.DATUM
    assert tokens[52].value == "8779.0"


version_lines = [
    # (text, number of versions)
    ("# Sample name: Blah blah", 0),
    ("# XDI/1.0", 1),
    ("# XDI/1.0 python/3.14.0", 2),
    ("# XDI/1.0 python/3.14.0 hollowfoot/2025.2rc23", 3),
]


@pytest.mark.parametrize("text,count", version_lines)
def test_version_pattern(text, count):
    match = version_pattern.match(text)
    if count == 0:
        pass
    else:
        assert match
        grp1, grp2 = match.groups()
        versions = [grp1, *grp2.strip().split(" ")]
        versions = [version for version in versions if version != ""]
        assert len(versions) == count


def test_parse_version():
    dataset = parse([Token("XDI/1.0", Role.VERSION), Token("GSE/1.3", Role.VERSION)])
    assert dataset.attrs["xdi_version"] == "1.0"
    assert dataset.attrs["version"]["GSE"] == "1.3"


def test_parse_header():
    dataset = parse(
        [
            Token("XDI/1.0", Role.VERSION),
            Token("Mono.d_spacing", Role.HEADER_NAME),
            Token("3.687", Role.HEADER_VALUE),
        ]
    )
    assert dataset.attrs["header"]["Mono.d_spacing"] == "3.687"


def test_parse_user_comment():
    dataset = parse(
        [
            Token("XDI/1.0", Role.VERSION),
            Token("spam", Role.USER_COMMENT),
            Token("and eggs", Role.USER_COMMENT),
        ]
    )
    assert dataset.attrs["user_comment"] == "spam\nand eggs"


def test_parse_column_labels():
    tokens = [
        Token("XDI/1.0", Role.VERSION),
        Token("mono-energy", Role.COLUMN_LABEL),
        Token("It-net_count", Role.COLUMN_LABEL),
    ]
    dataset = parse(tokens)
    assert list(dataset.coords.keys()) == ["mono-energy"]
    assert list(dataset.keys()) == ["It-net_count"]


def test_parse_data():
    tokens = [
        Token("XDI/1.0", Role.VERSION),
        Token("mono-energy", Role.COLUMN_LABEL),
        Token("It-net_count", Role.COLUMN_LABEL),
        Token("8333.0", Role.DATUM),
        Token("54893992", Role.DATUM),
    ]
    dataset = parse(tokens)
    np.testing.assert_equal(dataset["mono-energy"].values, [8333.0])
    np.testing.assert_equal(dataset["It-net_count"].values, [54893992])


def test_load():
    with open(xdi_path, mode="r") as fp:
        dataset = load(fp.read())
    assert isinstance(dataset, xr.Dataset)
    assert dataset.attrs["header"]["Facility.xray_source"] == "APS Undulator A"


def test_xarray_plugin():
    assert XDIBackendEntrypoint().guess_can_open(xdi_path)
    dataset = xr.open_dataset(xdi_path)
    assert isinstance(dataset, xr.Dataset)
    assert dataset.attrs["header"]["Facility.xray_source"] == "APS Undulator A"
