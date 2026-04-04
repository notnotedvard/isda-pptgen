"""
Generates a sample presentation using the pptx_builder module.
"""

from pptx import Presentation
from ppt_builder import *

presentation = Presentation("template.pptx")
insert_start_slide(presentation)
insert_simple_title_slide(presentation, "This is a simple title slide\nWhat if it has 2 lines?")
insert_title_with_logo_slide(presentation, "This is a title with a logo")
insert_video_slide(presentation, "example-files/gyp.mp4", "example-files/gyp-thumbnail.png", "Never Would I")
insert_image_slide(presentation, "example-files/gyp-thumbnail.png", "")
insert_chorus_slide(presentation, "Chorus", "This is text in a chorus slide\nit would naturally have\nmultiple lines\nright?")
insert_end_slide(presentation)

delete_template_slides(presentation)
presentation.save("example-files/output.pptx")
print("Test presentation generated successfully!")
