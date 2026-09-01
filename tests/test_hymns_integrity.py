import json
from pathlib import Path

import pytest

HYMNS_PATH = Path("assets/hymns.json")
MAX_LINE_LENGTH = 45


def load_hymns():
    if not HYMNS_PATH.exists():
        return []
    with open(HYMNS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


HYMNS_DATA = load_hymns()


@pytest.mark.parametrize("hymn", HYMNS_DATA, ids=lambda x: f"Hymn-{x['id']}")
def test_hymn_data_quality(hymn):
    """
    Validation logic migrated from problematic_hymn_finder.py.
    Checks for line lengths, whitespace, and block formatting.
    """
    hymn_id = hymn["id"]
    hymn_name = hymn.get("name", "Unknown")

    for block in hymn.get("lyrics", []):
        block_type = block.get("type", "Unknown").capitalize()
        block_label = block.get("label", "")
        text = block.get("text", "")
        identifier = f"{block_type} {block_label}".strip()

        lines = text.split("\n")
        for i, line in enumerate(lines):
            line_num = i + 1

            # Check 1: Line length
            assert len(line) <= MAX_LINE_LENGTH, (
                f"Hymn {hymn_id} ({hymn_name}): {identifier} line {line_num} too long ({len(line)} chars)"
            )

            # Check 2: Leading/trailing whitespace
            assert line.strip() == line, (
                f"Hymn {hymn_id} ({hymn_name}): {identifier} line {line_num} has leading/trailing whitespace"
            )

            # Check 3: Empty lines in middle of blocks
            if len(line) == 0:
                is_middle = i != 0 and i != len(lines) - 1
                assert not is_middle, (
                    f"Hymn {hymn_id} ({hymn_name}): {identifier} has an empty line in the middle"
                )

        # Check 4: Block length (visual limit for slides)
        assert len(lines) <= 10, (
            f"Hymn {hymn_id} ({hymn_name}): {identifier} has too many lines ({len(lines)})"
        )
