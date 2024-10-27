# Slide Generator
Automatic generation of powerpoint presentations from templates using python-pptx.

This generator supports the following in the template:
- Text
- Images
- Charts
- Maybe Tables

It definitely does not support videos or audio or any other complex objects.

check out `test.py` for an example and `hymn_lyrics_generator.py` which generates lyric slides for hymns using a database of hymn lyrics.

# DB structure
## Tables:
- hymns (id, name, author, major_key)
- refrains (hymn_id, refrain_text, refrain_position)
- verses (hymn_id, verse_text, verse_number)

## General syntax and information:
- `refrain_position` usually 1 (a refrain after every verse). It can be 0 (a refrain before the first verse and after every verse) or 2 (an alternative refrain after the last verse).
- `verse_text` and `refrain_text` can contain empty lines, indicating places where the verse can be split into two slides when the verse is too long.
- `author` and `major_key` are not complete.