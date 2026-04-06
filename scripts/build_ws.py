"""Generates a sample presentation using the pptx_builder module."""

import datetime
from pptx import Presentation

from isda_pptgen.builder import (
    delete_template_slides,
    insert_chorus_slide,
    insert_end_slide,
    insert_image_slide,
    insert_simple_title_slide,
    insert_scripture_slide,
    insert_start_slide,
    insert_title_with_logo_slide,
    insert_video_slide,
    insert_thithes_and_offerings_slides,
    merge_pptx,
)

def get_mission_spotlight_video():
    """Downloads the mission spotlight and returns the path to the video file and the thumbnail image."""
    return "example-files/gyp.mp4"

def get_yt_video(url:str):
    """Downloads the youtube video and returns the path to the video file and the thumbnail image."""
    return "example-files/gyp.mp4", "example-files/gyp-thumbnail.png"

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
preacher = "John Doe"
meditation_video = ""
closing_song_hymn = 633

presentation = Presentation("assets/template.pptx")
insert_start_slide(presentation, date)
insert_title_with_logo_slide(presentation, "Sabbath School Offering & Mission Spotlight")
insert_video_slide(presentation, get_mission_spotlight_video(), "example-files/gyp-thumbnail.png", "Mission Spotlight")
insert_title_with_logo_slide(presentation, "Song Service")
for hymn_number in song_service_hymns:
    insert_hymn(presentation, hymn_number)
insert_title_with_logo_slide(presentation, "Welcome and Announcements")
isert_images("announcements")
insert_title_with_logo_slide(presentation, "Call to Worship")
insert_scripture_slide(presentation, call_to_worship_scripture)
insert_title_with_logo_slide(presentation, "Opening Song")
insert_hymn(presentation, opening_song_hymn)
insert_title_with_logo_slide(presentation, "Intercessory Prayer")
insert_title_with_logo_slide(presentation, "Children's Story")
# (optional) insert children's story ppt
if childrens_story_ppt != "":
    merge_pptx(presentation, childrens_story_ppt)
insert_title_with_logo_slide(presentation, "Tithes and Offerings")
# (optional) isert thermometers
if thermometers_slides != "":
    merge_pptx(presentation, thermometers_slides)
insert_thithes_and_offerings_slides(presentation, unallocated_offerings)
insert_title_with_logo_slide(presentation, "Special Music")
if special_item_video != "":
    insert_video_slide(presentation, special_item_video, "example-files/gyp-thumbnail.png", "Special Music")
insert_title_with_logo_slide(presentation, "Scripture Reading")
insert_scripture_slide(presentation, scripture_reading)
insert_simple_title_slide(presentation, sermon_title) # should include preacher aswell
insert_title_with_logo_slide(presentation, "Meditation")
if meditation_video != "":
    insert_video_slide(presentation, meditation_video, "example-files/gyp-thumbnail.png", "Meditation")
insert_title_with_logo_slide(presentation, "Closing Song")
insert_hymn(presentation, closing_song_hymn)
insert_title_with_logo_slide(presentation, "Closing Prayer")
insert_title_with_logo_slide(presentation, "Closing Remarks")
insert_end_slide(presentation)
