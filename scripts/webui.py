import streamlit as st
import yaml
import shutil
import sys
import json
import contextlib
from pathlib import Path
import datetime
import copy

# Provide access to the scripts module if needed
sys.path.append(str(Path(".").resolve()))
from scripts.build_ws import build_presentation, get_filename
from scripts.fetch_schedule import fetch_data_for_date
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

original_config = copy.deepcopy(config)

if "field_sources" not in config:
    config["field_sources"] = {}
sources = config["field_sources"]

default_date = config.get("date", today)
if isinstance(default_date, str):
    try:
        default_date = datetime.date.fromisoformat(default_date)
    except ValueError:
        default_date = today

st.subheader(f"Service Date: {default_date.strftime('%B %d, %Y')}")

def fetch_for_date(d: datetime.date):
    for fmt in ["%d/%m/%Y", "%d/%m", "%m/%d/%Y", "%m/%d"]:
        data = fetch_data_for_date(d.strftime(fmt))
        if data: return data
    return None

def apply_fetched_data(data, keys=None):
    if not data:
        st.error("❌ No data found for this date in the Google Sheet. Make sure the date exists.")
        st.toast("No data found for this date in Google Sheet.", icon="❌")
        return False
        
    sv = data['service_details']
    so = data['song_details']
    
    def set_val(key, sheet_val, default_val):
        if keys and key not in keys: return
        final_val = sheet_val if str(sheet_val).strip() else default_val
        config[key] = final_val
        sources[key] = "sheet"
        # Update session_state safely because this function is now called BEFORE the widgets are instantiated
        st.session_state[key] = final_val
        
    def safe_hymn(v):
        if not str(v).strip(): return 0
        try: return int(str(v).strip())
        except: 
            v = str(v).strip()
            return v if v in all_hymn_nums else 0
            
    def safe_hymn_list(v1, v2):
        res = []
        for v in [v1, v2]:
            val = str(v).strip()
            if not val: continue
            try: res.append(int(val))
            except: res.append(val)
        return res

    set_val("preacher", sv.get("Preacher", ""), config.get("preacher", ""))
    set_val("sermon_title", sv.get("Sermon title", ""), config.get("sermon_title", ""))
    set_val("scripture_reading_reference", sv.get("Scripture reading reference", ""), config.get("scripture_reading_reference", ""))
    set_val("call_to_worship_scripture_reference", sv.get("Call to worship", ""), config.get("call_to_worship_scripture_reference", ""))
    set_val("unallocated_offerings", sv.get("Offerings", ""), config.get("unallocated_offerings", "Combined Budget"))
    
    set_val("opening_song_hymn", safe_hymn(so.get("Opening song", "")), config.get("opening_song_hymn", 0))
    set_val("closing_song_hymn", safe_hymn(so.get("Closing song", "")), config.get("closing_song_hymn", 0))
    
    h_list = safe_hymn_list(so.get("Song service song 1", ""), so.get("Song service song 2", ""))
    set_val("song_service_hymns", h_list, config.get("song_service_hymns", []))
    
    with open(program_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
    st.toast("Values updated from sheet!", icon="✅")
    return True

col_top1, col_top2 = st.columns([1, 1])
with col_top1:
    date_val = st.date_input("System Date", value=default_date, format="DD/MM/YYYY")

# Catch global fetch action immediately after date_val is instantiated
if st.session_state.get("fetch_all_btn"):
    data = fetch_for_date(date_val)
    apply_fetched_data(data)

if st.session_state.get("clear_all_btn"):
    keys_to_clear = [
        "preacher", "sermon_title", "scripture_reading_reference", 
        "call_to_worship_scripture_reference", "unallocated_offerings",
        "opening_song_hymn", "closing_song_hymn", "song_service_hymns",
        "mission_spotlight_url", "special_item_video_url", "meditation_video_url",
        "childrens_story_ppt", "sermon_slides", "thermometers_slides"
    ]
    for param in keys_to_clear:
        if param in ["opening_song_hymn", "closing_song_hymn"]:
            config[param] = 0
            sources[param] = "manual"
        elif param in ["song_service_hymns"]:
            config[param] = []
            sources[param] = "manual"
        elif param == "thermometers_slides":
            config[param] = "media/offerings.pptx"
            sources[param] = "manual"
        else:
            config[param] = ""
            sources[param] = "manual"
        
        if param in st.session_state:
            del st.session_state[param]
    
    with open(program_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    st.toast("All fields cleared!", icon="🧹")
    st.rerun()

def render_input(config_key, label, render_func, **kwargs):
    c1, c2 = st.columns([10, 1])
    
    # Catch per-field fetch action before widget is instantiated
    if st.session_state.get(f"fetch_btn_{config_key}"):
        data = fetch_for_date(date_val)
        apply_fetched_data(data, keys=[config_key])
        
    cur = config.get(config_key, kwargs.get("default"))
    if cur is None:
        cur = [] if render_func == st.multiselect else (0 if render_func == st.selectbox else "")

    # Check ahead in session_state so the UI label updates immediately on interaction
    if config_key in st.session_state:
        ss_val = st.session_state[config_key]
        if ss_val != cur and not st.session_state.get(f"fetch_btn_{config_key}") and not st.session_state.get("fetch_all_btn"):
            sources[config_key] = "manual"

    source = sources.get(config_key, "manual")
    ind = "Sourced from Google Sheet" if source == "sheet" else "Manual entry"
    full_label = f"{label} ({ind})"

    with c1:
        widget_kwargs = {"key": config_key}
        if config_key not in st.session_state:
            if render_func == st.text_input:
                widget_kwargs["value"] = cur
            elif render_func == st.selectbox:
                opts = kwargs["options"]
                widget_kwargs["index"] = opts.index(cur) if cur in opts else 0
            elif render_func == st.multiselect:
                opts = kwargs["options"]
                widget_kwargs["default"] = [x for x in cur if x in opts]

        if render_func == st.text_input:
            new_val = st.text_input(full_label, **widget_kwargs)
        elif render_func == st.selectbox:
            opts = kwargs["options"]
            new_val = st.selectbox(full_label, options=opts, format_func=kwargs.get("format_func"), **widget_kwargs)
        elif render_func == st.multiselect:
            opts = kwargs["options"]
            new_val = st.multiselect(full_label, options=opts, format_func=kwargs.get("format_func"), **widget_kwargs)
        else:
            new_val = cur

        if new_val != cur:
            if render_func == st.selectbox and new_val == 0 and config.get(config_key) is None:
                pass
            else:
                sources[config_key] = "manual"
                config[config_key] = new_val
                
    with c2:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        # We just render the button. We don't perform the logic here since we process the event at top of render_input.
        st.button("↺", key=f"fetch_btn_{config_key}", help=f"Fetch {label} from sheet")
                
    return new_val

with col_top2:
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    # Again, capture button clicks upstream.
    cb1, cb2 = st.columns([1, 1])
    with cb1:
        st.button("Fetch all from Google Sheet", key="fetch_all_btn")
    with cb2:
        st.button("🗑️ Clear All", key="clear_all_btn")


st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    mission_spotlight_url = st.text_input("Mission Spotlight URL", value=config.get("mission_spotlight_url", ""))

    song_service_hymns = render_input("song_service_hymns", "Song Service Hymns", st.multiselect, options=all_hymn_nums, default=[], format_func=format_hymn)
    call_to_worship_scripture_reference = render_input("call_to_worship_scripture_reference", "Call to Worship Scripture Reference", st.text_input, default="")
    opening_song_hymn = render_input("opening_song_hymn", "Opening Song", st.selectbox, options=hymn_options_with_none, default=0, format_func=format_hymn)
    
    st.markdown("---")
    current_childrens = config.get("childrens_story_ppt", "")
    cc1, cc2 = st.columns([4, 1])
    with cc1:
        st.write(f"**Current Children's Story:** `{current_childrens or 'None'}`")
    with cc2:
        if current_childrens and st.button("🗑️ Clear", key="clear_child"):
            config["childrens_story_ppt"] = ""
            current_childrens = ""
            with open(program_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            st.rerun()
    childrens_story_file = st.file_uploader("Upload PPT", type=["pptx", "ppt"], key="childrens_upload")

    special_item_video_url = st.text_input("Special Item Video URL", value=config.get("special_item_video_url", ""))

with col2:
    scripture_reading_reference = render_input("scripture_reading_reference", "Scripture Reading Reference", st.text_input, default="")
    sermon_title = render_input("sermon_title", "Sermon Title", st.text_input, default="")
    preacher = render_input("preacher", "Preacher", st.text_input, default="")
    
    st.markdown("---")
    current_sermon = config.get("sermon_slides", "")
    sc1, sc2 = st.columns([4, 1])
    with sc1:
        st.write(f"**Current Sermon Slides:** `{current_sermon or 'None'}`")
    with sc2:
        if current_sermon and st.button("🗑️ Clear", key="clear_sermon"):
            config["sermon_slides"] = ""
            current_sermon = ""
            with open(program_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            st.rerun()
    sermon_slides_file = st.file_uploader("Upload PPT", type=["pptx", "ppt"], key="sermon_upload")
    
    meditation_video_url = st.text_input("Meditation Video URL", value=config.get("meditation_video_url", ""))
    
    closing_song_hymn = render_input("closing_song_hymn", "Closing Song", st.selectbox, options=hymn_options_with_none, default=0, format_func=format_hymn)
    
    st.markdown("---")
    current_thermometers = config.get("thermometers_slides", "media/offerings.pptx")
    tc1, tc2 = st.columns([4, 1])
    with tc1:
        st.write(f"**Current Offering Thermometers:** `{current_thermometers}`")
    with tc2:
        # Default to media/offerings.pptx if none or cleared
        if current_thermometers and current_thermometers != "media/offerings.pptx" and st.button("🗑️ Clear", key="clear_thermometers"):
            config["thermometers_slides"] = "media/offerings.pptx"
            current_thermometers = "media/offerings.pptx"
            with open(program_path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            st.rerun()
    thermometers_slides_file = st.file_uploader("Upload Offering Thermometers PPT", type=["pptx", "ppt"], key="thermometers_upload")
    
    st.markdown("---")
    unallocated_offerings = render_input("unallocated_offerings", "Unallocated Offerings Line Item", st.text_input, default="Combined Budget")

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

new_thermometers_path = save_uploaded_file(thermometers_slides_file, date_str)
final_thermometers_slides = new_thermometers_path if new_thermometers_path else current_thermometers

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
    "thermometers_slides": final_thermometers_slides,
    "unallocated_offerings": unallocated_offerings,
    "membership_transfers": config.get("membership_transfers", []),
    "field_sources": sources
}

# Auto-save mechanism
if original_config != new_config:
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

st.markdown("---")
# Look for the generated output file to offer a download button
out_name = f"{get_filename(date_val)}.pptx"
out_file = Path("output") / out_name
if out_file.exists():
    with open(out_file, "rb") as f:
        st.download_button(
            label="📥 Download Generated Presentation",
            data=f,
            file_name=out_file.name,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            type="primary"
        )

