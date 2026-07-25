"""This script generates PowerPoint presentations with lyrics of hymns and external songs based on a template pptx file."""

import json
import os
import shutil
import time

from pptx import Presentation

from isda_pptgen.builder import (
    delete_template_slides,
    insert_external_song_by_id,
    insert_hymn,
)

HYMNS_JSON_PATH = "assets/hymns.json"
HYMNS_CACHE_PATH = "cache/hymns.json"
EXT_SONGS_JSON_PATH = "assets/external_songs.json"
EXT_SONGS_CACHE_PATH = "cache/external_songs.json"

with open(HYMNS_JSON_PATH, "r", encoding="utf-8") as f:
    HYMNS = json.load(f)

if os.path.exists(EXT_SONGS_JSON_PATH):
    with open(EXT_SONGS_JSON_PATH, "r", encoding="utf-8") as f:
        EXT_SONGS = json.load(f)
else:
    EXT_SONGS = []

NUMBER_OF_HYMNS = len(HYMNS)
NUMBER_OF_EXT_SONGS = len(EXT_SONGS)


def generate_hymn(number: int):
    """Generates slides for hymn number."""
    hymn_name = "Unknown"
    for hymn in HYMNS:
        if hymn["id"] == number:
            hymn_name = hymn["name"]
            break

    template = Presentation("assets/template.pptx")
    insert_hymn(template, number)
    delete_template_slides(template)
    template.save(f"hymns/{number:03} - {hymn_name}.pptx")


def generate_all_hymns(force_generate_all=False):
    start_time = time.time()

    CACHED_HYMNS = {}
    if os.path.exists(HYMNS_CACHE_PATH):
        try:
            with open(HYMNS_CACHE_PATH, "r", encoding="utf-8") as f:
                for ch in json.load(f):
                    CACHED_HYMNS[ch["id"]] = ch.get("lyrics", [])
        except json.JSONDecodeError:
            pass

    if not os.path.exists("hymns"):
        os.makedirs("hymns")

    total = len(HYMNS)
    generated = 0
    skipped = 0

    for i, hymn in enumerate(HYMNS, 1):
        hymn_number = hymn["id"]
        try:
            needs_gen = force_generate_all
            if not force_generate_all:
                hymn_lyrics = hymn.get("lyrics", [])
                hymn_cache = CACHED_HYMNS.get(hymn_number, [])
                needs_gen = hymn_lyrics != hymn_cache

            if needs_gen:
                generate_hymn(hymn_number)
                generated += 1
            else:
                skipped += 1

        except KeyboardInterrupt:
            print("\nProcess interrupted.")
            break

        print(
            f"\r  Hymns: {i}/{total} ({i * 100 // total}%)  "
            f"[generated {generated}, skipped {skipped}]",
            end="", flush=True,
        )

    print()  # newline after progress line
    print("Caching hymns json...")
    if not os.path.exists("cache"):
        os.makedirs("cache")
    shutil.copy(HYMNS_JSON_PATH, HYMNS_CACHE_PATH)

    print(f"Done in {time.time() - start_time:.2f} seconds.")


# ---------------------------------------------------------------------------
# External songs generation
# ---------------------------------------------------------------------------

def generate_external_song(ext_id: int):
    """Generates slides for an external song by its numeric ID.

    The title slide shows only the song name (no number prefix).  The ID is
    included in the output filename.
    """
    song_name = "Unknown"
    for song in EXT_SONGS:
        if song["id"] == ext_id:
            song_name = song["name"]
            break

    template = Presentation("assets/template.pptx")
    insert_external_song_by_id(template, ext_id)
    delete_template_slides(template)
    template.save(f"external_songs/{ext_id:03} - {song_name}.pptx")


def generate_all_external_songs(force_generate_all=False):
    if not EXT_SONGS:
        print("No external songs found. Skipping.")
        return

    start_time = time.time()

    CACHED_SONGS = {}
    if os.path.exists(EXT_SONGS_CACHE_PATH):
        try:
            with open(EXT_SONGS_CACHE_PATH, "r", encoding="utf-8") as f:
                for cs in json.load(f):
                    CACHED_SONGS[cs["id"]] = cs.get("lyrics", [])
        except json.JSONDecodeError:
            pass

    if not os.path.exists("external_songs"):
        os.makedirs("external_songs")

    total = len(EXT_SONGS)
    generated = 0
    skipped = 0

    for i, song in enumerate(EXT_SONGS, 1):
        song_id = song["id"]
        try:
            needs_gen = force_generate_all
            if not force_generate_all:
                song_lyrics = song.get("lyrics", [])
                song_cache = CACHED_SONGS.get(song_id, [])
                needs_gen = song_lyrics != song_cache

            if needs_gen:
                generate_external_song(song_id)
                generated += 1
            else:
                skipped += 1

        except KeyboardInterrupt:
            print("\nProcess interrupted.")
            break

        print(
            f"\r  Songs:  {i}/{total} ({i * 100 // total}%)  "
            f"[generated {generated}, skipped {skipped}]",
            end="", flush=True,
        )

    print()  # newline after progress line
    print("Caching external songs json...")
    if not os.path.exists("cache"):
        os.makedirs("cache")
    shutil.copy(EXT_SONGS_JSON_PATH, EXT_SONGS_CACHE_PATH)

    print(f"Done in {time.time() - start_time:.2f} seconds.")


if __name__ == "__main__":
    print(f"Found {NUMBER_OF_HYMNS} hymns, {NUMBER_OF_EXT_SONGS} external songs.")
    choice = input("Generate (h)ymns, (e)xternal songs, or (b)oth? [h/e/b]: ").strip().lower()

    if choice in ("h", "hymns", ""):
        force = input("Force generate all hymns? (y/N): ").strip().lower() == "y"
        generate_all_hymns(force)
    elif choice == "e":
        force = input("Force generate all external songs? (y/N): ").strip().lower() == "y"
        generate_all_external_songs(force)
    elif choice == "b":
        force = input("Force generate all? (y/N): ").strip().lower() == "y"
        generate_all_hymns(force)
        generate_all_external_songs(force)
    else:
        print("Invalid choice.")