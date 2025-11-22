import re
from collections.abc import Generator
from dataclasses import dataclass
from enum import Enum


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


field_end_pattern = re.compile(r"#\s*///+\s*")
header_end_pattern = re.compile(r"#\s*---+\s*")
version_pattern = re.compile(r"#\s*(XDI/[^ \t]+)((?:[ \t]+[^ \t/]+/[^ \t/]+)*)\s*")
header_pattern = re.compile(r"#\s*([^:]+):(.+)")
user_comment_pattern = re.compile(r"#\s*(.*)")
space_separated_pattern = re.compile("[^ \t]+")  # Individual labels, not the whole line


def xdi_to_tokens(text: str) -> Generator[Token]:
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
