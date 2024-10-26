"""Utility script to find problematic hymns in the database. This may include:
- hymns with verse lines / refrain lines longer that MAX_LINE_LENGHT characters

TODO:
hymns with missing verses
"""

import sqlite3
import os

MAX_LINE_LENGHT = 45
MAX_VERSE_LENGTH = 1000
problematic_hymns = {} # {hymn_id: [problem1, problem2, ...]}
DB_PATH = 'hymns.sqlite'
if not os.path.exists(DB_PATH):
    print(f"Database file {DB_PATH} not found.")
    exit()

db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

def add_problematic_hymn(hymn_number:int, problem_to_add:str):
    """Add a hymn to the problematic_hymns dictionary."""
    if hymn_number not in problematic_hymns:
        problematic_hymns[hymn_number] = [problem_to_add]
    else:
        problematic_hymns[hymn_number].append(problem_to_add)

cursor.execute("SELECT * FROM verses") # (hymn_id, verse_text, verse_number)
verse_elements = cursor.fetchall()
cursor.execute("SELECT * FROM refrains") # (hymn_id, refrain_text, refrain_position)
refrain_elements = cursor.fetchall()

elements = []

for element in verse_elements:
    elements.append(list(element) + ["Verse"])
for element in refrain_elements:
    elements.append(list(element) + ["Refrain"])

for element in enumerate(elements):
    element_hymn_number = element[1][0]
    element_type = element[1][3]
    HAS_MORE_THAN_8_LINES_FLAG = False
    HAS_MANUAL_SPLIT_FLAG = False # if the verse has been manually split, it does not need to be counted as having more than 8 lines
    for line_number, line in enumerate(element[1][1].split("\n")): # split the text into lines
        if len(line) > MAX_LINE_LENGHT: # if line is longer than MAX_LINE_LENGHT characters
            # pass
            add_problematic_hymn(element_hymn_number, f"{element_type} {element[1][2]} line {line_number+1} is too long. ({len(line)} characters)")
        if line.strip() != line: # if line has leading/trailing whitespace
            # pass
            add_problematic_hymn(element_hymn_number, f"{element_type} {element[1][2]} line {line_number+1} has leading/trailing whitespace.")

        if len(line) == 0:
            if line_number != 0 and line_number != len(element[1][1].split("\n")) - 1: # if line is empty and it's not the first or last line
                HAS_MANUAL_SPLIT_FLAG = True
            else:
                wording = "start" if line_number == 0 else "end"
                add_problematic_hymn(element_hymn_number, f"{element_type} {element[1][2]} has an empty line at {wording}.")
        
        if line_number > 7 and not HAS_MORE_THAN_8_LINES_FLAG and not HAS_MANUAL_SPLIT_FLAG: # if the verse has more than 8 lines amd it's the first time it's detected
            HAS_MORE_THAN_8_LINES_FLAG = True
            add_problematic_hymn(element_hymn_number, f"{element_type} {element[1][2]} has more than 8 lines.")


# showing the problematic hymns
problematic_hymns = dict(sorted(problematic_hymns.items()))

for hymn_id, problems in problematic_hymns.items():
    cursor.execute("SELECT name FROM hymns WHERE id = ?", (hymn_id,))
    title = cursor.fetchone()[0]
    print(f"Hymn {hymn_id} ({title}):")
    for problem in problems:
        print(f"\033[2m  - {problem}\033[0m")

number_of_problems = sum([len(problems) for problems in problematic_hymns.values()])
print(f"{number_of_problems} problems ({len(problematic_hymns)}) problematic hymns.")
