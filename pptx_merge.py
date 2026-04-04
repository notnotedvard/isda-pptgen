"""Utilities to merge .pptx files into an existing presentation."""

from pptx import Presentation

from slide_duplication_utility import (
    _object_rels,
    _exp_add_slide,
    copy_shapes,
    remove_shape,
)


def merge_pptx(target: Presentation, source_path: str) -> None:
    """
    Merge all slides from a source .pptx file into a target presentation.

    :param target: The target Presentation to merge into
    :param source_path: Path to the source .pptx file to merge
    """
    source = Presentation(source_path)

    # Get a blank layout from target (use index 6 - blank layout)
    target_blank_layout = target.slide_layouts[6]

    for src_slide in source.slides:
        # Add blank slide to target using TARGET's layout
        dest = _exp_add_slide(target, target_blank_layout)

        # Remove all shapes from the default layout
        for shape in dest.shapes:
            remove_shape(shape)

        # Copy all existing shapes from source
        copy_shapes(src_slide.shapes, dest)

        # Copy existing references (hyperlinks, etc.)
        known_refs = [
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        ]
        for rel in _object_rels(src_slide.part):
            if rel.reltype in known_refs:
                if rel.is_external:
                    dest.part.rels.get_or_add_ext_rel(rel.reltype, rel._target)
                else:
                    dest.part.rels.get_or_add(rel.reltype, rel._target)

        # Copy notes if present
        if src_slide.has_notes_slide:
            txt = src_slide.notes_slide.notes_text_frame.text
            dest.notes_slide.notes_text_frame.text = txt