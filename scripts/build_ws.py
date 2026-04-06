"""Generates a sample presentation using the pptx_builder module."""

import datetime
from pptx import Presentation

from isda_pptgen.builder import (
    clear_media_folder,
    delete_template_slides,
    insert_chorus_slide,
    insert_end_slide,
    insert_hymn,
    insert_image_slide,
    insert_images,
    insert_scripture_slide,
    insert_simple_title_slide,
    insert_start_slide,
    insert_title_with_logo_slide,
    insert_video_slide,
    insert_thithes_and_offerings_slides,
)

from isda_pptgen.ytdl import download_youtube_video, merge_subtitles, burn_subtitles
from isda_pptgen.merge import merge_pptx
import os

# Worship service details
date = datetime.date.fromisoformat("2024-06-15")
mission_spotlight_url = "https://www.youtube.com/watch?v=OznS1gAwe0c"
song_service_hymns = [526, 526]
call_to_worship_scripture_reference = "Psalm 147:1"
opening_song_hymn = 473
childrens_story_ppt = ""
thermometers_slides = ""
unallocated_offerings = "Something"
special_item_video_url = "https://www.youtube.com/watch?v=QeS0z1_cpNI"
scripture_reading_reference = "John 3:16"
sermon_title = "God's Free Health Plan"
sermon_slides = ""
preacher = "John Doe"
meditation_video_url = ""
closing_song_hymn = 633

presentation = Presentation("assets/template.pptx")
# clear_media_folder()

# # Downloading and preparing media
# if mission_spotlight_url != "":
#     download_youtube_video(mission_spotlight_url, output_dir="media", filename="mission-spotlight", download_subtitles=True)
#     burn_subtitles("media/mission-spotlight.mp4", "media/mission-spotlight.en.srt", "media/mission-spotlight-subbed.mp4")
# if special_item_video_url != "":
#     download_youtube_video(special_item_video_url, output_dir="media", filename="special-item", download_subtitles=False)
# if meditation_video_url != "":
#     download_youtube_video(meditation_video_url, output_dir="media", filename="meditation", download_subtitles=False)

# fetch scripture
call_to_worship_scripture = (
        ("1", "This is the first verse."),
        ("2", "This is the second verse."),
        ("3", "This is the third verse.")
    )
scripture_reading = (
        ("1", "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."),
    )

# start slides
insert_start_slide(presentation, date)
insert_title_with_logo_slide(presentation, "Sabbath School Offering & Mission Spotlight")

# mission spotlight
insert_video_slide(presentation, "media/mission-spotlight-subbed.mp4", "media/mission-spotlight.png", "Mission Spotlight")

# song service
insert_title_with_logo_slide(presentation, "Song Service")
for hymn_number in song_service_hymns:
    insert_hymn(presentation, hymn_number)

# announcements
insert_title_with_logo_slide(presentation, "Welcome and Announcements")
announcement_dir = "media/announcements"
if os.path.exists(announcement_dir):
    images = tuple(sorted([os.path.join(announcement_dir, f) for f in os.listdir(announcement_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]))
    insert_images(presentation, images)
# merge_pptx(presentation, "media/announcements/announcements.pptx")

# opening song
insert_title_with_logo_slide(presentation, "Call to Worship")
insert_scripture_slide(presentation, call_to_worship_scripture_reference, call_to_worship_scripture)
insert_title_with_logo_slide(presentation, "Opening Song")
insert_hymn(presentation, opening_song_hymn)

# intercessory prayer
insert_title_with_logo_slide(presentation, "Intercessory Prayer")

# children's story
insert_title_with_logo_slide(presentation, "Children's Story")
if childrens_story_ppt != "":
    merge_pptx(presentation, childrens_story_ppt)

# tithes and offerings
insert_title_with_logo_slide(presentation, "Tithes and Offerings")
if thermometers_slides != "":
    merge_pptx(presentation, thermometers_slides)
insert_thithes_and_offerings_slides(presentation, unallocated_offerings)

# special music
insert_title_with_logo_slide(presentation, "Special Music")
if special_item_video_url != "":
    insert_video_slide(presentation, "media/special-item.mp4", "media/special-item.png")

# scripture reading
insert_title_with_logo_slide(presentation, "Scripture Reading")
insert_scripture_slide(presentation, scripture_reading_reference, scripture_reading)

# sermon
insert_simple_title_slide(presentation, f"Sermon : {sermon_title}") # should include preacher aswell
if sermon_slides != "":
    merge_pptx(presentation, sermon_slides)

insert_title_with_logo_slide(presentation, "Meditation")
if meditation_video_url != "":
    insert_video_slide(presentation, "media/meditation.mp4", "media/meditation.png")

# closing song
insert_title_with_logo_slide(presentation, "Closing Song")
insert_hymn(presentation, closing_song_hymn)

# closing
insert_title_with_logo_slide(presentation, "Closing Prayer")
insert_title_with_logo_slide(presentation, "Closing Remarks")
insert_end_slide(presentation)

delete_template_slides(presentation)
presentation.save("output/ws_output.pptx")
print("Presentation generated successfully!")
