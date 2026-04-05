"""This script generates a PowerPoint presentation with the lyrics of a hymn based on a template pptx file."""

import os
import shutil
import sqlite3
import time

from pptx import Presentation

from ppt_builder import (
    delete_template_slides,
    insert_hymn,
)

DB = sqlite3.connect("hymns.sqlite")
CACHED_DB = sqlite3.connect("cache/hymns.sqlite")
cursor = DB.cursor()
cached_cursor = CACHED_DB.cursor()
NUMBER_OF_HYMNS = cursor.execute("SELECT COUNT(*) FROM hymns").fetchone()[0]

def generate_hymn(number:int):
    """Genrates slides for hymn number"""
    hymn_name = cursor.execute("SELECT name FROM hymns WHERE id = ?", (number,)).fetchone()[0]

    # creating a presentation
    template = Presentation("template.pptx")
    
    insert_hymn(template, number)

    delete_template_slides(template)
    template.save(f"hymns/{number:03} - {hymn_name}.pptx")

FORCE_GENERATE_ALL = input("force generate all ? (y/N): ") == "y"
start_time = time.time()

for hymn_number in range(1, NUMBER_OF_HYMNS + 1):
    try:
        if FORCE_GENERATE_ALL:
            generate_hymn(hymn_number)
        else:
            # compare hymn number (hymn_number) from cache and hymn from db and generate if they are different
            hymn_db = cursor.execute("SELECT * FROM verses WHERE hymn_id = ? UNION ALL SELECT * FROM refrains WHERE hymn_id = ?", (hymn_number, hymn_number)).fetchall()
            hymn_cache = cached_cursor.execute("SELECT * FROM verses WHERE hymn_id = ? UNION ALL SELECT * FROM refrains WHERE hymn_id = ?", (hymn_number, hymn_number)).fetchall()

            if hymn_db != hymn_cache:
                generate_hymn(hymn_number)

            # generate the hymn if the pptx file does not exist
            # look for pptx files that start with hymn_number - ... .pptx
            # if not any(fname.startswith(f"{hymn_number:03} - ") and fname.endswith(".pptx") for fname in os.listdir("hymns")):
            #     generate_hymn(hymn_number)
    except KeyboardInterrupt:
        print("Process interrupted.")
        break

print("Caching db...")
# make a copy in cache/hymns.sqlite
if not os.path.exists("cache"):
    os.makedirs("cache")
shutil.copy("hymns.sqlite", "cache/hymns.sqlite")

print(f"Done in {time.time() - start_time:.2f} seconds.")
