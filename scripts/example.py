"""Generates a sample presentation using the pptx_builder module."""

import datetime
from pptx import Presentation

from isda_pptgen.ppt_builder import (
    delete_template_slides,
    insert_chorus_slide,
    insert_end_slide,
    insert_hymn,
    insert_image_slide,
    insert_simple_title_slide,
    insert_start_slide,
    insert_title_with_logo_slide,
    insert_video_slide,
    merge_pptx,
)

date = datetime.datetime.now()
presentation = Presentation("assets/template.pptx")
insert_start_slide(presentation, date)
insert_simple_title_slide(presentation, "This is a simple title slide\nWhat if it has 2 lines?")
insert_title_with_logo_slide(presentation, "This is a title with a logo")
insert_simple_title_slide(presentation, "Here I will merge another presentation")
merge_pptx(presentation, "assets/template.pptx")
insert_video_slide(presentation, "example-files/gyp.mp4", "example-files/gyp-thumbnail.png", "Never Would I")
insert_image_slide(presentation, "example-files/gyp-thumbnail.png", "")
insert_chorus_slide(presentation, "Chorus", "This is text in a chorus slide\nit would naturally have\nmultiple lines\nright?")
insert_hymn(presentation, 12)
insert_end_slide(presentation)

delete_template_slides(presentation)
presentation.save("example-files/output.pptx")
print("Test presentation generated successfully!")
