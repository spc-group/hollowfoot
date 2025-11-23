from pathlib import Path

import numpy as np
import pytest

from hollowfoot.xdi import Role, Token, parse, tokenize, version_pattern


def test_tokenizer():
    with open(Path(__file__).parent / "example.xdi", mode="r") as fp:
        tokens = list(tokenize(fp.read()))

    assert tokens[0].role == Role.VERSION
    assert tokens[0].value == "XDI/1.0"
    assert tokens[1].role == Role.HEADER_NAME
    assert tokens[1].value == "Column.1"
    assert tokens[31].role == Role.USER_COMMENT
    assert tokens[31].value == "Goal: do some measurements"
    expected_columns = [
        "I0_ds-count",
        "It_ds-count",
        "Iref_ds-count",
        "Ipreslit-count",
        "IpreKB_ds-count",
        "I0_ds-count_rate",
        "It_ds-count_rate",
        "Iref_ds-count_rate",
        "Ipreslit-count_rate",
        "monochromator-bragg",
        "IpreKB_ds-count_rate",
        "monochromator-energy",
    ]
    column_labels = tokens[32:44]
    assert [col.role for col in column_labels] == [Role.COLUMN_LABEL] * len(
        expected_columns
    )
    assert [col.value for col in column_labels] == expected_columns
    assert tokens[44].role == Role.DATUM
    assert tokens[44].value == "395896964.3102694"


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
    dataset = parse([Token("XDI/1.0", Role.VERSION)])
    assert dataset.attrs["xdi_version"] == "1.0"


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
