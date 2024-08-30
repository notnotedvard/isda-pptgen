"""
Me trying to learn how to generate powerpoint slides using python
"""

from pptx import Presentation
from pptx_builder import *

presentation = Presentation("template.pptx")
insert_video_slide(presentation, "gyp.mp4", "Never Would I")
insert_image_slide(presentation, "gyp-thumbnail.png", "")
insert_simple_title_slide(presentation, "This is a simple title slide\nWhat if it has 2 lines?")
insert_chorus_slide(presentation, "Chorus", "This is text in a chorus slide\nit would naturally have\nmultiple lines\nright?")
insert_end_slide(presentation)

delete_template_slides(presentation)
presentation.save("output.pptx")
