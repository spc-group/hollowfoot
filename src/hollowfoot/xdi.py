import ast
import re
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from enum import Enum
from typing import Any

import xarray as xr


class XDIMalformed(Exception):
    pass


class Role(int, Enum):
    VERSION = 0
    HEADER_NAME = 1
    HEADER_VALUE = 2
    USER_COMMENT = 3
    COLUMN_LABEL = 4
    DATUM = 5


@dataclass()
class Token:
    value: str
    role: Role


number_pattern = re.compile("[-_0-9.e]+")


def as_number(value: str) -> float | int:
    # Make sure only valid number characters are present
    if number_pattern.match(value):
        return ast.literal_eval(value)
    else:
        return float("nan")


field_end_pattern = re.compile(r"#\s*///+\s*")
header_end_pattern = re.compile(r"#\s*---+\s*")
version_pattern = re.compile(r"#\s*(XDI/[^ \t]+)((?:[ \t]+[^ \t/]+/[^ \t/]+)*)\s*")
header_pattern = re.compile(r"#\s*([^:]+):(.+)")
user_comment_pattern = re.compile(r"#\s*(.*)")
space_separated_pattern = re.compile("[^ \t]+")  # Individual labels, not the whole line


def tokenize(text: str) -> Generator[Token]:
    """Lexxer that turns an XDI formatted text into Line tokens."""
    current_section = "version"
    for line in text.split("\n"):
        # Check for field- and header-end lines
        if match := field_end_pattern.match(line):
            current_section = "user_comments"
            continue
        elif match := header_end_pattern.match(line):
            current_section = "data"
            continue
        # Check for a version line
        elif current_section == "version" and (match := version_pattern.match(line)):
            current_section = "header"
            grp1, grp2 = match.groups()
            versions = [grp1, *grp2.strip().split(" ")]
            versions = [version for version in versions if version != ""]
            yield from (Token(ver, Role.VERSION) for ver in versions)
            continue
        # Check for header fields
        elif current_section == "header" and (match := header_pattern.match(line)):
            name, value = match.groups()
            yield Token(name.strip(), Role.HEADER_NAME)
            yield Token(value.strip(), Role.HEADER_VALUE)
            continue
        # Check for user comments
        elif current_section == "user_comments" and (
            match := user_comment_pattern.match(line)
        ):
            yield Token(match.group(1), Role.USER_COMMENT)
        # Column labels
        elif current_section == "data" and line.startswith("#"):
            for match in space_separated_pattern.finditer(line.lstrip("#")):
                yield Token(match.group(), Role.COLUMN_LABEL)
        elif current_section == "data":
            for match in space_separated_pattern.finditer(line):
                yield Token(match.group(), Role.DATUM)
        else:
            raise XDIMalformed(line)


def parse(tokens: Iterable[Token]) -> xr.Dataset:
    tokens_ = iter(tokens)
    attrs: dict[str, Any] = {}
    labels = []
    data = []
    # Check that the XDI version is first
    token = next(tokens_)
    if token.role == Role.VERSION and token.value.startswith("XDI/"):
        attrs["xdi_version"] = token.value.split("/")[1]
    else:
        raise XDIMalformed(f"Invalid version token {token}.")
    # Process the rest of the tokens
    while True:
        try:
            token = next(tokens_)
        except StopIteration:
            break
        if token.role == Role.HEADER_NAME:
            # Header name, so next token should be the value
            headers = attrs.setdefault("header", {})
            headers[token.value] = next(tokens_).value
        elif token.role == Role.USER_COMMENT:
            # Combine user comments
            previous_comment = attrs.get("user_comment", "")
            comment = "\n".join([previous_comment, token.value]).strip("\n")
            attrs["user_comment"] = comment
        elif token.role == Role.COLUMN_LABEL:
            labels.append(token.value)
        elif token.role == Role.DATUM:
            data.append(as_number(token.value))
        else:
            raise XDIMalformed(f"Unknown token role: {token}")
    # Align the data with their column labels
    if len(labels) == 0:
        coords = {}
        data_vars = {}
    else:
        coords = {labels[0]: data[:: len(labels)]}
        dv = {
            label: data[idx + 1 :: len(labels)] for idx, label in enumerate(labels[1:])
        }
        data_vars = {label: (coords.keys(), data) for label, data in dv.items()}
    return xr.Dataset(
        coords=coords,
        data_vars=data_vars,
        attrs=attrs,
    )
