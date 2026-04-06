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


date = datetime.date.fromisoformat("2024-06-15")
song_service_hymns = [526, 526]
call_to_worship_scripture = "Psalm 147:1"
opening_song_hymn = 473
childrens_story_ppt = ""
thermometers_slides = ""
unallocated_offerings = "Combined Budget"
special_item_video = "example-files/gyp.mp4"
scripture_reading = "John 3:16"
sermon_title = "God's Free Health Plan"
sermon_slides = ""
preacher = "John Doe"
meditation_video = ""
closing_song_hymn = 633

presentation = Presentation("assets/template.pptx")

# start slides
insert_start_slide(presentation, date)
insert_title_with_logo_slide(presentation, "Sabbath School Offering & Mission Spotlight")

# mission spotlight
insert_video_slide(presentation, get_mission_spotlight_video(), "example-files/gyp-thumbnail.png", "Mission Spotlight")

# song service
insert_title_with_logo_slide(presentation, "Song Service")
for hymn_number in song_service_hymns:
    insert_hymn(presentation, hymn_number)

# announcements
insert_title_with_logo_slide(presentation, "Welcome and Announcements")
insert_images("announcements")

# opening song
insert_title_with_logo_slide(presentation, "Call to Worship")
insert_scripture_slide(presentation, call_to_worship_scripture)
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
if special_item_video != "":
    insert_video_slide(presentation, special_item_video, "example-files/gyp-thumbnail.png", "Special Music")

# scripture reading
insert_title_with_logo_slide(presentation, "Scripture Reading")
insert_scripture_slide(presentation, scripture_reading)

# sermon
insert_simple_title_slide(presentation, f"Sermon : {sermon_title}") # should include preacher aswell
if sermon_slides != "":
    merge_pptx(presentation, sermon_slides)

insert_title_with_logo_slide(presentation, "Meditation")
if meditation_video != "":
    insert_video_slide(presentation, meditation_video, "example-files/gyp-thumbnail.png", "Meditation")

# closing song
insert_title_with_logo_slide(presentation, "Closing Song")
insert_hymn(presentation, closing_song_hymn)

# closing
insert_title_with_logo_slide(presentation, "Closing Prayer")
insert_title_with_logo_slide(presentation, "Closing Remarks")
insert_end_slide(presentation)
