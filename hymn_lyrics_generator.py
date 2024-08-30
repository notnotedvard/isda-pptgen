"""This script generates a PowerPoint presentation with the lyrics of a hymn based on a template pptx file."""

import sqlite3
from pptx_builder import *
from pptx import Presentation
import time

db = sqlite3.connect('../SMMS/external_data/hymns.sqlite')
cursor = db.cursor()
number_of_hymns = cursor.execute("SELECT COUNT(*) FROM hymns").fetchone()[0]
start_time = time.time()
print(f"Number of hymns: {number_of_hymns}")

for hymn_number in range(1, number_of_hymns + 1):
    try:
        # getting the data from the database
        hymn_name = cursor.execute("SELECT name FROM hymns WHERE id = ?", (hymn_number,)).fetchone()[0]
        print(f"Generating slides for hymn #{hymn_number:03}: {hymn_name}")
        cursor.execute('SELECT verse_text, verse_number FROM verses WHERE hymn_id = ? ORDER BY verse_number', (hymn_number,))
        verses = cursor.fetchall()
        cursor.execute('SELECT refrain_text, refrain_position FROM refrains WHERE hymn_id = ? ORDER BY refrain_position', (hymn_number,))
        refrains = cursor.fetchall()

        # creating a presentation
        template = Presentation("template.pptx")
        insert_song_title_slide(template, hymn_number, hymn_name)
        
        if len(refrains) == 0: # if there are no refrains, add verses one by one
            for verse in verses[:-1]:
                insert_chorus_slide(template, verse[1], verse[0])
            insert_chorus_slide(template, verses[-1][1], verses[-1][0], True)
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
                    insert_chorus_slide(template, "Refrain", refrain[0])
                    hymn_refrain = refrain[0]
                elif refrain[1] == 1:
                    hymn_refrain = refrain[0]
                elif refrain[1] == 2:
                    end_refrain = refrain[0]
            for verse_index, verse in enumerate(verses):
                insert_chorus_slide(template, verse[1], verse[0])
                if verse_index == len(verses) - 1:
                    if end_refrain != "":
                        # if it's the last verse and there's an end refrain
                        insert_chorus_slide(template, "Refrain", end_refrain, True)
                    else:
                        # if it's the last verse and there's no end refrain
                        insert_chorus_slide(template, "Refrain", hymn_refrain, True)
                else:
                    # if everything is normal
                    insert_chorus_slide(template, "Refrain", hymn_refrain)




        delete_template_slides(template)
        template.save(f"hymns/{hymn_number:03} - {hymn_name}.pptx")
    except KeyboardInterrupt:
        print("Process interrupted.")
        break

print(f"Done in {time.time() - start_time:.2f} seconds.")
