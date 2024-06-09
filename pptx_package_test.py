"""
Me trying to learn how to generate powerpoint slides using python
"""

from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from utilities import *

presentation = Presentation("template.pptx")
insert_video_slide(presentation, "gyp.mp4", "Never Would I")
insert_image_slide(presentation, "gyp-thumbnail.png", "")
insert_simple_title_slide(presentation, "This is a simple title slide")
insert_end_slide(presentation)

delete_template_slides(presentation)
presentation.save("output.pptx")
