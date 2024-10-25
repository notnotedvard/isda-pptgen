"""
Generates a sample presentation using the pptx_builder module.
"""

from pptx import Presentation
from pptx_builder import *

presentation = Presentation("template.pptx")
insert_simple_title_slide(presentation, "This is a simple title slide\nWhat if it has 2 lines?")
insert_video_slide(presentation, "example-files/gyp.mp4", "example-files/gyp-thumbnail.png", "Never Would I")
insert_image_slide(presentation, "example-files/gyp-thumbnail.png", "")
insert_chorus_slide(presentation, "Chorus", "This is text in a chorus slide\nit would naturally have\nmultiple lines\nright?")
insert_end_slide(presentation)

delete_template_slides(presentation)
presentation.save("example-files/output.pptx")
