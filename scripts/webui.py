import streamlit as st
import yaml
import shutil
import sys
import json
import contextlib
from pathlib import Path
import datetime

# Provide access to the scripts module if needed
sys.path.append(str(Path(".").resolve()))
from scripts.build_ws import build_presentation
import time

st.set_page_config(page_title="ISDA PPT Generator", layout="wide")
st.title("ISDA PPT Generator")

PROGRAMS_DIR = Path("configs")
PROGRAMS_DIR.mkdir(exist_ok=True)
MEDIA_DIR = Path("media")
MEDIA_DIR.mkdir(exist_ok=True)
TEMPLATE_FILE = Path("scripts/build_ws.template.yml")
if not TEMPLATE_FILE.exists():
    TEMPLATE_FILE = Path("scripts/build_ws.yml")

# --- Load Hymns for Autocomplete ---
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

def format_hymn(hymn_num):
    if hymn_num == 0 or hymn_num == "0":
        return "None / Skip"
    return hymn_dict.get(hymn_num, str(hymn_num))

all_hymn_nums = list(hymn_dict.keys())
hymn_options_with_none = [0] + all_hymn_nums

# --- Auto-Generate Next 2 Saturdays ---
today = datetime.date.today()
days_to_sat = 5 - today.weekday()
if days_to_sat < 0:
    days_to_sat += 7
next_sat = today + datetime.timedelta(days=days_to_sat)
following_sat = next_sat + datetime.timedelta(days=7)

for sat in [next_sat, following_sat]:
    file_name = f"{sat.isoformat()}_Service.yml"
    file_path = PROGRAMS_DIR / file_name
    if not file_path.exists() and TEMPLATE_FILE.exists():
        shutil.copy(TEMPLATE_FILE, file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            conf = yaml.safe_load(f) or {}
        conf["date"] = sat
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(conf, f, default_flow_style=False, sort_keys=False)

# --- UI Sidebar: Programs List ---
st.sidebar.header("Upcoming Services")
program_files = sorted(list(PROGRAMS_DIR.glob("*.yml")) + list(PROGRAMS_DIR.glob("*.yaml")))
program_names = [f.name for f in program_files]

if not program_names:
    st.warning("No template found.")
    st.stop()

selected_program = st.sidebar.radio("Select to Edit", program_names)

# --- Main Content Area ---
program_path = PROGRAMS_DIR / selected_program
with open(program_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f) or {}

default_date = config.get("date", today)
if isinstance(default_date, str):
    try:
        default_date = datetime.date.fromisoformat(default_date)
    except ValueError:
        default_date = today

st.subheader(f"Service Date: {default_date.strftime('%B %d, %Y')}")

col1, col2 = st.columns(2)

with col1:
    date_val = st.date_input("System Date", value=default_date)
    mission_spotlight_url = st.text_input("Mission Spotlight URL", value=config.get("mission_spotlight_url", ""))
    
    current_hymns = config.get("song_service_hymns", [])
    if not isinstance(current_hymns, list):
        current_hymns = []
    
    song_service_hymns = st.multiselect(
        "Song Service Hymns", 
        options=all_hymn_nums,
        default=[h for h in current_hymns if h in all_hymn_nums],
        format_func=format_hymn
    )
    
    call_to_worship_scripture_reference = st.text_input("Call to Worship Scripture Reference", value=config.get("call_to_worship_scripture_reference", ""))
    
    op_song = config.get("opening_song_hymn", 0)
    if op_song is None: op_song = 0
    opening_song_hymn = st.selectbox(
        "Opening Song", 
        options=hymn_options_with_none,
        index=hymn_options_with_none.index(op_song) if op_song in hymn_options_with_none else 0,
        format_func=format_hymn
    )
    
    st.markdown("---")
    current_childrens = config.get("childrens_story_ppt", "")
    st.write(f"**Current Children's Story:** `{current_childrens or 'None'}`")
    childrens_story_file = st.file_uploader("Upload PPT", type=["pptx", "ppt"], key="childrens_upload")

    special_item_video_url = st.text_input("Special Item Video URL", value=config.get("special_item_video_url", ""))

with col2:
    scripture_reading_reference = st.text_input("Scripture Reading Reference", value=config.get("scripture_reading_reference", ""))
    sermon_title = st.text_input("Sermon Title", value=config.get("sermon_title", ""))
    preacher = st.text_input("Preacher", value=config.get("preacher", ""))
    
    st.markdown("---")
    current_sermon = config.get("sermon_slides", "")
    st.write(f"**Current Sermon Slides:** `{current_sermon or 'None'}`")
    sermon_slides_file = st.file_uploader("Upload PPT", type=["pptx", "ppt"], key="sermon_upload")
    
    meditation_video_url = st.text_input("Meditation Video URL", value=config.get("meditation_video_url", ""))
    
    cl_song = config.get("closing_song_hymn", 0)
    if cl_song is None: cl_song = 0
    closing_song_hymn = st.selectbox(
        "Closing Song", 
        options=hymn_options_with_none,
        index=hymn_options_with_none.index(cl_song) if cl_song in hymn_options_with_none else 0,
        format_func=format_hymn
    )
    
    thermometers_slides = st.text_input("Offering Thermometers Slides Path", value=config.get("thermometers_slides", "media/offerings.pptx"))
    unallocated_offerings = st.text_input("Unallocated Offerings Line Item", value=config.get("unallocated_offerings", "Combined Budget"))

st.markdown("---")
col_b, col_dl = st.columns([1, 4])
with col_dl:
    download_media = st.checkbox("Download Media?", value=config.get("download_media", False))
with col_b:
    generate = st.button("Generate PPT", type="primary")

# Function to save uploaded file
def save_uploaded_file(uploaded_file, date_str):
    if uploaded_file is not None:
        target_dir = MEDIA_DIR / date_str
        target_dir.mkdir(exist_ok=True, parents=True)
        file_path = target_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return str(file_path)
    return None

date_str = date_val.isoformat()
new_childrens_path = save_uploaded_file(childrens_story_file, date_str)
final_childrens_story_ppt = new_childrens_path if new_childrens_path else current_childrens

new_sermon_path = save_uploaded_file(sermon_slides_file, date_str)
final_sermon_slides = new_sermon_path if new_sermon_path else current_sermon

new_config = {
    "date": date_val,
    "mission_spotlight_url": mission_spotlight_url,
    "song_service_hymns": song_service_hymns,
    "call_to_worship_scripture_reference": call_to_worship_scripture_reference,
    "opening_song_hymn": opening_song_hymn if opening_song_hymn not in [0, "0"] else None,
    "childrens_story_ppt": final_childrens_story_ppt,
    "scripture_reading_reference": scripture_reading_reference,
    "sermon_title": sermon_title,
    "preacher": preacher,
    "sermon_slides": final_sermon_slides,
    "special_item_video_url": special_item_video_url,
    "meditation_video_url": meditation_video_url,
    "closing_song_hymn": closing_song_hymn if closing_song_hymn not in [0, "0"] else None,
    "download_media": download_media,
    "thermometers_slides": thermometers_slides,
    "unallocated_offerings": unallocated_offerings,
    "membership_transfers": config.get("membership_transfers", [])
}

# Auto-save mechanism
if config != new_config:
    with open(program_path, "w", encoding="utf-8") as f:
        yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
    # Streamlit reruns on state change, so it auto-renders the rest
    msg = st.sidebar.empty()
    msg.write("Changes saved!")
    time.sleep(2)
    msg.empty()


class StreamToStreamlit:
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.text = ""

    def write(self, data):
        if isinstance(data, str):
            parts = data.split('\r')
            for i, part in enumerate(parts):
                if i > 0:
                    # clear the current line
                    last_newline = self.text.rfind('\n')
                    if last_newline != -1:
                        self.text = self.text[:last_newline + 1]
                    else:
                        self.text = ""
                self.text += part
            # Keep the last 5000 characters to prevent Streamlit UI lag
            self.placeholder.code(self.text[-5000:], language="plaintext")

    def flush(self):
        pass

    def isatty(self):
        return False

if generate:
    st.markdown("### Generation Logs")
    log_placeholder = st.empty()
    out_stream = StreamToStreamlit(log_placeholder)

    with st.spinner("Building presentation..."):
        with contextlib.redirect_stdout(out_stream), contextlib.redirect_stderr(out_stream):
            try:
                build_presentation(new_config)
                st.success("Presentation generated successfully!", icon="✅")
            except Exception as e:
                st.error(f"Error generating presentation: {str(e)}")

