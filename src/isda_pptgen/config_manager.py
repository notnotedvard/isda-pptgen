import datetime
import difflib
import json
import logging
from pathlib import Path

import yaml

from isda_pptgen.fetch_schedule import fetch_data_for_date

logger = logging.getLogger(__name__)


def get_next_saturday() -> datetime.date:
    """Returns the date of the upcoming Saturday."""
    today = datetime.date.today()
    days_ahead = 5 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + datetime.timedelta(days_ahead)


def setup_hymndict():
    hymn_dict = {}

    try:
        with open("assets/hymns.json", "r", encoding="utf-8") as f:
            hymns_data = json.load(f)
            for h in hymns_data:
                hymn_dict[h["id"]] = f"{h['id']} - {h['name']}"
    except FileNotFoundError:
        pass

    try:
        with open("assets/external_songs.json", "r", encoding="utf-8") as f:
            ext_data = json.load(f)
            for h in ext_data:
                key = f"ext_{h['id']}"
                hymn_dict[key] = f"[Ext] {h['id']} - {h['name']}"
    except FileNotFoundError:
        pass

    return hymn_dict


def safe_hymn(v, hymn_dict):
    val = str(v).strip()
    if not val:
        return 0

    all_hymn_nums = list(hymn_dict.keys())

    try:
        h_num = int(val)
        if h_num in all_hymn_nums:
            return h_num
    except Exception:
        pass

    if val in all_hymn_nums:
        return val

    song_names = list(hymn_dict.values())
    if not song_names:
        return 0

    matches = difflib.get_close_matches(val, song_names, n=1, cutoff=0.6)
    if matches:
        matched_name = matches[0]
        for k, name in hymn_dict.items():
            if name == matched_name:
                return k

    return 0


def fetch_for_date(d: datetime.date):
    for fmt in ["%d/%m/%Y", "%d/%m", "%m/%d/%Y", "%m/%d", "%Y-%m-%d"]:
        data = fetch_data_for_date(d.strftime(fmt))
        if data:
            return data
    return None


def populate_config(config_path: Path, date_str: str):
    """Populates empty fields in the YAML from Google Sheet and warns on conflicts."""
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f) or {}

    try:
        d = datetime.date.fromisoformat(date_str)
    except ValueError:
        logger.error(
            f"Invalid date format in config filename: {date_str}. Expected YYYY-MM-DD."
        )
        return

    sheet_data = fetch_for_date(d)
    if not sheet_data:
        logger.warning(f"No data found in Google Sheets for date {d}.")
        return

    sv = sheet_data.get("service_details", {})

    hymn_dict = setup_hymndict()
    has_changes = False

    def update_field(key, new_value, is_list=False):
        nonlocal has_changes
        config_value = config_data.get(key)

        # Determine if config field is 'empty'
        is_empty = False
        if config_value is None or config_value == "" or is_list and not config_value:
            is_empty = True

        if is_empty:
            if new_value:
                config_data[key] = new_value
                has_changes = True
                logger.info(f"Populated field '{key}' with '{new_value}'")
        else:
            # Field is not empty and conflicts with populated sheet
            # We ignore cases where new_value is virtually empty (like 0 for hymns)
            if new_value and new_value != config_value:
                logger.warning(
                    f"Conflict for '{key}': Config has '{config_value}', "
                    f"but Sheet has '{new_value}'. Kept config value."
                )

    update_field("preacher", sv.get("Preacher", ""))
    update_field("sermon_title", sv.get("Sermon title", ""))
    update_field("scripture_reading_reference", sv.get("Bible verse", ""))
    update_field("call_to_worship_scripture_reference", sv.get("Call to worship", ""))
    update_field("unallocated_offerings", sv.get("Offerings", ""))

    o_hymn = safe_hymn(sv.get("Opening song", ""), hymn_dict)
    if o_hymn != 0:
        update_field("opening_song_hymn", o_hymn)

    c_hymn = safe_hymn(sv.get("Closing song", ""), hymn_dict)
    if c_hymn != 0:
        update_field("closing_song_hymn", c_hymn)

    ss_hymns = []
    sh1 = safe_hymn(sv.get("Song service song 1", ""), hymn_dict)
    sh2 = safe_hymn(sv.get("Song service song 2", ""), hymn_dict)
    if sh1 != 0:
        ss_hymns.append(sh1)
    if sh2 != 0:
        ss_hymns.append(sh2)

    if ss_hymns:
        update_field("song_service_hymns", ss_hymns, is_list=True)

    if has_changes:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config_data, f, sort_keys=False, allow_unicode=True)
        logger.info("Configuration updated successfully.")
    else:
        logger.info("No empty fields required populating.")


def cmd_create(populate: bool):
    """Creates a config file for the upcoming Saturday."""
    date = get_next_saturday()
    date_str = date.strftime("%Y-%m-%d")
    config_dir = Path("configs")
    config_dir.mkdir(exist_ok=True)

    file_path = config_dir / f"{date_str}_Service.yml"

    if not file_path.exists():
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump({"date": date_str}, f, sort_keys=False, allow_unicode=True)
        logger.info(f"Created empty config: {file_path}")
    else:
        logger.info(f"Config file already exists: {file_path}")

    if populate:
        logger.info("Populating with Google Sheet data...")
        populate_config(file_path, date_str)


def cmd_populate(config_path: Path):
    # Extract the date from filename (Assuming YYYY-MM-DD format prefix)
    date_str = config_path.name[:10]
    populate_config(config_path, date_str)
