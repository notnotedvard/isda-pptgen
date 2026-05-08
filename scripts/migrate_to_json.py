import json
import os
import sqlite3
import sys

DB_PATH = "assets/hymns.sqlite"
JSON_PATH = "assets/sda-hymns/hymns.json"

if not os.path.exists(DB_PATH):
    print(f"Database file {DB_PATH} not found.")
    sys.exit(1)

db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

# Get all hymns
cursor.execute("SELECT id, name, author, major_key FROM hymns ORDER BY id")
hymns_data = cursor.fetchall()

hymns_export = []

for hymn_row in hymns_data:
    hymn_id, name, author, major_key = hymn_row
    
    # Get Verses
    cursor.execute("SELECT verse_number, verse_text FROM verses WHERE hymn_id = ? ORDER BY verse_number", (hymn_id,))
    verses = cursor.fetchall()
    
    # Get Refrains
    cursor.execute("SELECT refrain_position, refrain_text FROM refrains WHERE hymn_id = ? ORDER BY refrain_position", (hymn_id,))
    refrains = cursor.fetchall()

    lyrics_blocks = []
    
    # Merge and order them according to the old system's logic:
    # refrain_position 0 -> start of hymn
    # refrain_position 1 -> after each verse
    # refrain_position 2 -> at the end
    
    start_refrain = None
    standard_refrain = None
    end_refrain = None

    for pos, text in refrains:
        if pos == 0:
            start_refrain = text
            standard_refrain = text
        elif pos == 1:
            standard_refrain = text
        elif pos == 2:
            end_refrain = text

    if start_refrain is not None:
        lyrics_blocks.append({"type": "refrain", "label": "Chorus", "text": start_refrain})

    for i, (v_num, v_text) in enumerate(verses):
        lyrics_blocks.append({"type": "verse", "label": f"{v_num}", "text": v_text})
        
        is_last = i == (len(verses) - 1)
        if is_last:
            if end_refrain is not None:
                lyrics_blocks.append({"type": "refrain", "label": "Chorus", "text": end_refrain})
            elif standard_refrain is not None:
                lyrics_blocks.append({"type": "refrain", "label": "Chorus", "text": standard_refrain})
        else:
            if standard_refrain is not None:
                lyrics_blocks.append({"type": "refrain", "label": "Chorus", "text": standard_refrain})

    hymn_dict = {
        "id": hymn_id,
        "name": name,
        "author": author if author else None,
        "key": major_key if major_key else None,
        "lyrics": lyrics_blocks
    }
    
    hymns_export.append(hymn_dict)

with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(hymns_export, f, indent=2, ensure_ascii=False)

print(f"Successfully migrated {len(hymns_export)} hymns to {JSON_PATH}!")
