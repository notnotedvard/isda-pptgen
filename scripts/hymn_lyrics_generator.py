"""This script generates a PowerPoint presentation with the lyrics of a hymn based on a template pptx file."""

import json
import os
import shutil
import time

from pptx import Presentation

from isda_pptgen.builder import (
    delete_template_slides,
    insert_hymn,
)

JSON_PATH = "assets/hymns.json"
CACHE_PATH = "cache/hymns.json"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    HYMNS = json.load(f)

NUMBER_OF_HYMNS = len(HYMNS)

def generate_hymn(number:int):
    """Genrates slides for hymn number"""
    hymn_name = "Unknown"
    for hymn in HYMNS:
        if hymn["id"] == number:
            hymn_name = hymn["name"]
            break

    # creating a presentation
    template = Presentation("assets/template.pptx")
    
    insert_hymn(template, number)

    delete_template_slides(template)
    template.save(f"hymns/{number:03} - {hymn_name}.pptx")

FORCE_GENERATE_ALL = input("force generate all ? (y/N): ") == "y"
start_time = time.time()

# Load cache to compare
CACHED_HYMNS = {}
if os.path.exists(CACHE_PATH):
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            for ch in json.load(f):
                CACHED_HYMNS[ch["id"]] = ch.get("lyrics", [])
    except json.JSONDecodeError:
        pass

if not os.path.exists("hymns"):
    os.makedirs("hymns")

for hymn in HYMNS:
    hymn_number = hymn["id"]
    try:
        if FORCE_GENERATE_ALL:
            generate_hymn(hymn_number)
        else:
            # compare hymn lyrics from cache and hymn from JSON
            hymn_lyrics = hymn.get("lyrics", [])
            hymn_cache = CACHED_HYMNS.get(hymn_number, [])

            if hymn_lyrics != hymn_cache:
                generate_hymn(hymn_number)

    except KeyboardInterrupt:
        print("Process interrupted.")
        break

print("Caching json...")
if not os.path.exists("cache"):
    os.makedirs("cache")
shutil.copy(JSON_PATH, CACHE_PATH)

print(f"Done in {time.time() - start_time:.2f} seconds.")
