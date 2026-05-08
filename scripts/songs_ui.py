import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="ISDA Song Manager", layout="wide")
st.title("Song Manager")

HYMNS_FILE = Path("assets/sda-hymns/hymns.json")
EXT_SONGS_FILE = Path("assets/external_songs.json")

def load_data(file_path):
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

st.sidebar.header("Select Source")
source_type = st.sidebar.radio("Source", ["Hymns", "External Songs"])

current_file = HYMNS_FILE if source_type == "Hymns" else EXT_SONGS_FILE
songs_data = load_data(current_file)

# Sorting by ID if present
songs_data = sorted(songs_data, key=lambda x: x.get("id", 0))

# Sidebar: Select/Create Song
song_options = ["--- Create New Song ---"] + [f"{s.get('id', '')} - {s.get('name', 'Untitled')}" for s in songs_data]
selected_song_str = st.sidebar.selectbox("Select a song", song_options)

if selected_song_str == "--- Create New Song ---":
    st.header("Create New Song")
    new_id = st.number_input("ID", value=max([s.get("id", 0) for s in songs_data] + [0]) + 1, step=1)
    new_name = st.text_input("Name")
    new_author = st.text_input("Author", value="")
    new_key = st.text_input("Key", value="")
    
    if st.button("Create"):
        new_song = {
            "id": new_id,
            "name": new_name,
            "author": new_author if new_author else None,
            "key": new_key if new_key else None,
            "lyrics": []
        }
        songs_data.append(new_song)
        save_data(current_file, songs_data)
        st.success(f"Created {new_name}!")
        st.rerun()

else:
    # Find selected song
    sel_id = int(selected_song_str.split(" - ")[0])
    song_idx = next((i for i, s in enumerate(songs_data) if s.get("id") == sel_id), None)
    
    if song_idx is not None:
        song = songs_data[song_idx]
        st.header(f"Edit: {song.get('name')}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            song_name = st.text_input("Name", value=song.get("name", ""))
        with col2:
            song_author = st.text_input("Author", value=song.get("author", "") or "")
        with col3:
            song_key = st.text_input("Key", value=song.get("key", "") or "")
            
        st.subheader("Lyrics")
        lyrics = song.get("lyrics", [])
        updated_lyrics = []
        
        for i, block in enumerate(lyrics):
            with st.expander(f"Block {i+1}: {block.get('label', '')} ({block.get('type', '')})", expanded=True):
                bc1, bc2 = st.columns([1, 1])
                with bc1:
                    b_type = st.text_input(f"Type (verse/refrain/etc) {i}", value=block.get("type", ""), key=f"type_{i}")
                with bc2:
                    b_label = st.text_input(f"Label (1, Chorus, etc) {i}", value=block.get("label", ""), key=f"label_{i}")
                
                b_text = st.text_area(f"Text {i}", value=block.get("text", ""), key=f"text_{i}", height=250)
                
                if st.button(f"Remove Block {i+1}", key=f"rm_{i}"):
                    continue # Skip appending this block
                
                updated_lyrics.append({
                    "type": b_type,
                    "label": b_label,
                    "text": b_text
                })
                
        if st.button("Add New Block"):
            updated_lyrics.append({
                "type": "verse",
                "label": str(len(updated_lyrics) + 1),
                "text": ""
            })
            song["lyrics"] = updated_lyrics
            songs_data[song_idx] = song
            save_data(current_file, songs_data)
            st.rerun()
            
        st.markdown("---")
        
        c_save, c_del = st.columns(2)
        with c_save:
            if st.button("Save Changes", type="primary"):
                song["name"] = song_name
                song["author"] = song_author if song_author else None
                song["key"] = song_key if song_key else None
                song["lyrics"] = updated_lyrics
                songs_data[song_idx] = song
                save_data(current_file, songs_data)
                st.success("Changes saved!")
                st.rerun()
                
        with c_del:
            if st.button("Delete Song", type="primary"):
                songs_data.pop(song_idx)
                save_data(current_file, songs_data)
                st.warning("Song deleted!")
                st.rerun()
