# ISDA PPT Generator

Automatic generation of PowerPoint presentations from templates using python-pptx.

This generator supports the following in the template:
- Text
- Images
- Charts
- Maybe Tables

It definitely does not support videos or audio or any other complex objects.

## Setup

This project uses `uv` for dependency management. To set up the project and install the CLI hook:

```bash
uv sync
```

## Usage (CLI)

The project provides a command-line interface `isda-pptgen`. You can run it via `uv`:

```bash
uv run isda-pptgen --help
```

### Available Commands

- **Build Worship Service Slides:**
  ```bash
  uv run isda-pptgen build-ws --config configs/ws.yml
  ```
- **Generate Hymn Lyrics:**
  ```bash
  uv run isda-pptgen generate-lyrics [--force]
  ```

*Note: You can also check out the standalone script examples in the `scripts/` directory (e.g., `scripts/example.py` or `scripts/hymn_lyrics_generator.py`).*

## Project Structure

- `src/isda_pptgen/` - Core library modules and CLI entry point (`main.py`).
- `scripts/` - Standalone utility scripts for debugging or direct use.
- `configs/` - YAML configuration files (e.g., `ws.yml`).
- `assets/` - Static assets like `template.pptx` and the `hymns.sqlite` database.

## DB Structure (`assets/hymns.sqlite`)
### Tables:
- hymns (id, name, author, major_key)
- refrains (hymn_id, refrain_text, refrain_position)
- verses (hymn_id, verse_text, verse_number)

### General syntax and information:
- `refrain_position` usually 1 (a refrain after every verse). It can be 0 (a refrain before the first verse and after every verse) or 2 (an alternative refrain after the last verse).
- `verse_text` and `refrain_text` can contain empty lines, indicating places where the verse can be split into two slides when the verse is too long.
- `author` and `major_key` are not complete.