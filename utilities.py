"""This module contains utility functions that are used for creating the slides."""

from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import copy

VIDEO_WITH_CAPTION_SLIDE = 1
SIMPLE_TITLE_SLIDE = 2
SONG_TITLE_SLIDE = 3
CHORUS_SLIDE = 4
VERSE_SLIDE = 5

def insert_custom_run(pragraph, text:str, size:int, colored:bool=False):
    """Creates a run with following settings:
    - font size: 32pt (0), 44pt (1), 60pt (2)
    - font color: white or rgb(242, 207, 248) (colored)
    - font name: Loos Normal Medium
    - alignment: center
    Does not return anything, modifies the paragraph object directly.
    """
    text = str(text)

    match size:
        case 0:
            font_size = Pt(32)
        case 1:
            font_size = Pt(44)
        case 2:
            font_size = Pt(60)
        case _: # default
            font_size = Pt(60)

    custom_run = pragraph.add_run()
    custom_run.text = text
    custom_run.font.size = font_size
    custom_run.font.color.rgb = RGBColor(242, 207, 248) if colored else RGBColor(255, 255, 255)
    custom_run.font.name = "Loos Normal Medium"
    custom_run.alignment = PP_ALIGN.CENTER

def duplicate_slide(presentation, slide_index):
    """Duplicates a slide and returns the new slide."""
    slide_to_duplicate = presentation.slides[slide_index]
    layout = slide_to_duplicate.slide_layout
    new_slide = presentation.slides.add_slide(layout)

    for shape in slide_to_duplicate.shapes:
        el = shape.element
        new_el = copy.deepcopy(el)
        new_slide.shapes._spTree.insert_element_before(new_el, 'p:extLst')
        
    return new_slide

def delete_template_slides(presentation:Presentation):
    """Deletes the template slides from the presentation."""
    # delete the 7 first slides
    for _ in range(7):
        presentation.slides._sldIdLst.remove(presentation.slides._sldIdLst[0])


def insert_song_title_slide(presentation:Presentation, number:int, title:str):
    """Inserts a slide with the title of the song."""
    number = str(f"{number:03}")
    slide = duplicate_slide(presentation, SONG_TITLE_SLIDE)

    # modify the contents of the slide
    for shape in slide.shapes:
        if shape.name == "song_title":
            shape.text_frame.clear()
            title_paragraph = shape.text_frame.add_paragraph()
            title_paragraph.alignment = PP_ALIGN.CENTER
            insert_custom_run(title_paragraph, f"#{number}", size=0, colored=False)
            insert_custom_run(title_paragraph, f"\n{title}", size=2, colored=False)

def insert_chorus_slide(presentation:Presentation, verse_name:str, text:str, last_slide:bool=False):
    """Inserts a slide with the chorus of the song."""
    slide = duplicate_slide(presentation, CHORUS_SLIDE)

    # modify the contents of the slide
    for shape in slide.shapes:
        if shape.name == "chorus":
            shape.text_frame.clear()
            chorus_paragraph = shape.text_frame.add_paragraph()
            chorus_paragraph.alignment = PP_ALIGN.CENTER
            insert_custom_run(chorus_paragraph, verse_name, size=0, colored=True)
            insert_custom_run(chorus_paragraph, f"\n{text}", size=1, colored=False)

    if last_slide:
        # get size of the slide in inches
        posx = Inches(presentation.slide_width.inches) - Inches(0.8)
        posy = Inches(presentation.slide_height.inches) - Inches(0.8)

        # add the square
        square = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, posx, posy, Inches(0.4), Inches(0.4))
        square.fill.solid()
        square.fill.fore_color.rgb = RGBColor(255, 255, 255)
        # remove outline
        square.line.fill.background()

