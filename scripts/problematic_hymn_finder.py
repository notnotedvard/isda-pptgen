"""
Utility script to find problematic hymns in the JSON database. This may include:
- hymns with verse lines / refrain lines longer that MAX_LINE_LENGHT characters
"""

import os
import json
import sys

MAX_LINE_LENGHT = 45
MAX_VERSE_LENGTH = 1000
problematic_hymns = {} # {hymn_id: [problem1, problem2, ...]}
JSON_PATH = "assets/sda-hymns/hymns.json"
if not os.path.exists(JSON_PATH):
    print(f"JSON file {JSON_PATH} not found. Did you run the migration script?")
    sys.exit()

def add_problematic_hymn(hymn_number:int, problem_to_add:str):
    """Add a hymn to the problematic_hymns dictionary."""
    if hymn_number not in problematic_hymns:
        problematic_hymns[hymn_number] = [problem_to_add]
    else:
        problematic_hymns[hymn_number].append(problem_to_add)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    hymns_data = json.load(f)

hymn_titles = {}

for hymn in hymns_data:
    hymn_id = hymn["id"]
    hymn_titles[hymn_id] = hymn.get("name", "Unknown Title")
    
    HAS_MORE_THAN_8_LINES_FLAG = False
    
    for block in hymn.get("lyrics", []):
        block_type = block.get("type", "Unknown").capitalize()
        block_label = block.get("label", "")
        text = block.get("text", "")
        
        identifier = f"{block_type} {block_label}".strip()
        HAS_MANUAL_SPLIT_FLAG = False
        
        lines = text.split("\n")
        for line_number, line in enumerate(lines):
            if len(line) > MAX_LINE_LENGHT:
                add_problematic_hymn(hymn_id, f"{identifier} line {line_number+1} is too long. ({len(line)} characters)")
            if line.strip() != line:
                add_problematic_hymn(hymn_id, f"{identifier} line {line_number+1} has leading/trailing whitespace.")

            if len(line) == 0:
                if line_number != 0 and line_number != len(lines) - 1:
                    HAS_MANUAL_SPLIT_FLAG = True
                else:
                    wording = "start" if line_number == 0 else "end"
                    add_problematic_hymn(hymn_id, f"{identifier} has an empty line at {wording}.")

            if line_number > 7 and not HAS_MORE_THAN_8_LINES_FLAG and not HAS_MANUAL_SPLIT_FLAG:
                HAS_MORE_THAN_8_LINES_FLAG = True
                add_problematic_hymn(hymn_id, f"{identifier} has more than 8 lines.")

# showing the problematic hymns
problematic_hymns = dict(sorted(problematic_hymns.items()))

for hymn_id, problems in problematic_hymns.items():
    title = hymn_titles.get(hymn_id, "Unknown Title")
    print(f"Hymn {hymn_id} ({title}):")
    for problem in problems:
        print(f"\033[2m  - {problem}\033[0m")

number_of_problems = sum([len(problems) for problems in problematic_hymns.values()])
print(f"{number_of_problems} problems ({len(problematic_hymns)}) problematic hymns.")
