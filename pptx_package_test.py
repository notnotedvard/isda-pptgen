"""
Me trying to learn how to generate powerpoint slides using python
"""

from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from utilities import *

# Defining constants
TITLE_LAYOUT = 0
TITLE_AND_CONTENT_LAYOUT = 1
SECTION_HEADER_LAYOUT = 2
TWO_CONTENT_LAYOUT = 3
COMPARISON_LAYOUT = 4
TITLE_ONLY_LAYOUT = 5
BLANK_LAYOUT = 6
CONTENT_WITH_CAPTION_LAYOUT = 7
PICTURE_WITH_CAPTION_LAYOUT = 8


# Create a presentation object
prs = Presentation("template.pptx")

# # select the first slide
# first_slide = prs.slides[0]
# first_slide_title = first_slide.shapes.title
# # change font of the title
# first_slide_title_text_frame = first_slide_title.text_frame
# run = first_slide_title_text_frame.paragraphs[0].add_run()
# run.text = "LAKJKLJLKSJDKLAJ?"
# font = run.font
# font.color.rgb = RGBColor(0xFF, 0x7F, 0x50)

# # Add a slide to the presentation
# my_slide_layout = prs.slide_layouts[TITLE_LAYOUT]
# slide = prs.slides.add_slide(my_slide_layout)

# # Add text to the slide
# title = slide.shapes.title
# title.text = "asdasdasd, World!"

# # Add a subtitle to the slide
# subtitle = slide.placeholders[1]
# subtitle.text = "This is a subtitle"

insert_chorus_slide(prs, "Verse 1", "This is a verse")
insert_chorus_slide(prs, "Refrain", "This is the last refrain", True)

delete_template_slides(prs)


# Save the presentation
prs.save("output.pptx")