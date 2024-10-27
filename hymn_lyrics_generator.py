"""This script generates a PowerPoint presentation with the lyrics of a hymn based on a template pptx file."""

import os
import time
import shutil
import sqlite3
from pptx import Presentation
from pptx_builder import *

DB = sqlite3.connect('hymns.sqlite')
CACHED_DB = sqlite3.connect('cache/hymns.sqlite')
cursor = DB.cursor()
cached_cursor = CACHED_DB.cursor()
NUMBER_OF_HYMNS = cursor.execute("SELECT COUNT(*) FROM hymns").fetchone()[0]

def generate_hymn(number:int):
    """genrates slides for hymn number"""
    # getting the data from the database
    hymn_name = cursor.execute("SELECT name FROM hymns WHERE id = ?", (number,)).fetchone()[0]
    print(f"Generating slides for hymn #{number:03}: {hymn_name}")
    cursor.execute('SELECT verse_text, verse_number FROM verses WHERE hymn_id = ? ORDER BY verse_number', (number,))
    verses = cursor.fetchall()
    cursor.execute('SELECT refrain_text, refrain_position FROM refrains WHERE hymn_id = ? ORDER BY refrain_position', (number,))
    refrains = cursor.fetchall()

    # creating a presentation
    template = Presentation("template.pptx")
    insert_song_title_slide(template, number, hymn_name)
    
    if len(refrains) == 0: # if there are no refrains, add verses one by one
        for verse in verses[:-1]:
            insert_smart_chorus_slide(template, verse[1], verse[0])
        insert_smart_chorus_slide(template, verses[-1][1], verses[-1][0], True)
    else:
        # act according to refrain positions
        # 0 indicates that the hymn starts with a refrain (ex: ?)
        # 1 indicates that the hymn has a refrain after each verse
        # 2 indicates that the hymn has a different refrain at the end (ex: 140)
        # -> a hymn can have multiple refrains, but only one of each type

        end_refrain = "" # used if the end refrain is different from the other refrains
        hymn_refrain = ""
        for refrain in refrains:
            if refrain[1] == 0:
                insert_smart_chorus_slide(template, "Refrain", refrain[0])
                hymn_refrain = refrain[0]
            elif refrain[1] == 1:
                hymn_refrain = refrain[0]
            elif refrain[1] == 2:
                end_refrain = refrain[0]
        for verse_index, verse in enumerate(verses):
            insert_smart_chorus_slide(template, verse[1], verse[0])
            if verse_index == len(verses) - 1:
                if end_refrain != "":
                    # if it's the last verse and there's an end refrain
                    insert_smart_chorus_slide(template, "Refrain", end_refrain, True)
                else:
                    # if it's the last verse and there's no end refrain
                    insert_smart_chorus_slide(template, "Refrain", hymn_refrain, True)
            else:
                # if everything is normal
                insert_smart_chorus_slide(template, "Refrain", hymn_refrain)

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
    except KeyboardInterrupt:
        print("Process interrupted.")
        break

print("Caching db...")
# make a copy in cache/hymns.sqlite
if not os.path.exists('cache'):
    os.makedirs('cache')
shutil.copy('hymns.sqlite', 'cache/hymns.sqlite')

print(f"Done in {time.time() - start_time:.2f} seconds.")
