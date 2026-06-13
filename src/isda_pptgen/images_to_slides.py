"""Generate a PowerPoint presentation from images in the current directory."""

import os
import re
import tempfile
from pathlib import Path
from PIL import Image

from pptx import Presentation

from isda_pptgen.builder import delete_template_slides, insert_image_slide

# Formats supported by python-pptx
SUPPORTED_PPTX_FORMATS = {"JPEG", "PNG", "GIF", "BMP", "TIFF", "WMF"}
# Extensions to scan for
IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif")


def natural_sort_key(path: Path):
    """Generate a sort key that handles numbers in filenames naturally."""
    # Extract number from filename for sorting (e.g., "Slide 1" -> 1, "IMG_0369" -> 369)
    name = path.stem  # filename without extension
    # Look for any number in the filename
    numbers = re.findall(r'\d+', name)
    if numbers:
        # Return a tuple: (filename with numbers zero-padded, the number itself)
        # This makes "Slide2" come after "Slide1", not before "Slide10"
        return (re.sub(r'\d+', lambda m: m.group(0).zfill(10), name.lower()), int(numbers[0]))
    return (name.lower(), 0)


def convert_to_jpeg(image_path: Path) -> str:
    """Convert an image to JPEG format, returning the path to the converted file."""
    output_dir = tempfile.gettempdir()
    output_path = os.path.join(output_dir, f"{image_path.stem}_converted.jpg")
    
    with Image.open(image_path) as im:
        # Convert to RGB if necessary (e.g., RGBA -> RGB)
        if im.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", im.size, (255, 255, 255))
            if im.mode == "P":
                im = im.convert("RGBA")
            background.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
            im = background
        elif im.mode != "RGB":
            im = im.convert("RGB")
        
        # Save as JPEG
        im.save(output_path, "JPEG", quality=95)
    
    return output_path


def generate_from_images(output: str = "images_presentation.pptx", caption: str = "", extensions=IMAGE_EXTENSIONS, directory: str = None):
    """
    Generate a PowerPoint presentation from images in the current directory.
    
    Args:
        output: Output file name
        caption: Caption to add to each slide
        extensions: Tuple of image extensions to include
        directory: Directory to scan for images (default: current directory)
    """
    current_dir = Path(directory) if directory else Path.cwd()
    images = []
    
    # Find all images with the specified extensions
    for ext in extensions:
        images.extend(sorted(current_dir.glob(f"*.{ext}")))
        images.extend(sorted(current_dir.glob(f"*{ext.upper()}")))
    
    # Remove duplicates and filter/convert unsupported formats
    seen = set()
    unique_images = []
    skipped_formats = {}
    converted_count = 0
    
    for img in images:
        if img.name.lower() in seen:
            continue
        
        # Try to detect actual format and convert if needed
        try:
            with Image.open(img) as im:
                fmt = im.format
                if fmt not in SUPPORTED_PPTX_FORMATS:
                    # Try to convert unsupported formats to JPEG
                    if fmt == "MPO":
                        converted_path = convert_to_jpeg(img)
                        unique_images.append(Path(converted_path))
                        converted_count += 1
                        seen.add(img.name.lower())
                        continue
                    skipped_formats[fmt] = skipped_formats.get(fmt, 0) + 1
                    continue
        except Exception as e:
            skipped_formats["unreadable"] = skipped_formats.get("unreadable", 0) + 1
            continue
        
        seen.add(img.name.lower())
        unique_images.append(img)
    
    if converted_count > 0:
        print(f"Converted {converted_count} image(s) to JPEG")
    for fmt, count in skipped_formats.items():
        print(f"Skipped {count} image(s) with unsupported format: {fmt}")
    
    # Natural sort - handles "Slide1, Slide2, Slide10" correctly
    images = sorted(unique_images, key=natural_sort_key)
    
    # Filter out very large images (> 50MB) to avoid memory issues
    max_size_mb = 50
    filtered_images = [img for img in images if img.stat().st_size <= max_size_mb * 1024 * 1024]
    skipped = len(images) - len(filtered_images)
    if skipped > 0:
        print(f"Skipped {skipped} image(s) larger than {max_size_mb}MB")
    images = filtered_images
    
    if not images:
        print("No images found in the current directory!")
        return
    
    print(f"Found {len(images)} image(s)")
    
    # Load template
    template_path = Path(__file__).parent.parent.parent / "assets" / "template.pptx"
    if not template_path.exists():
        print(f"Template not found at {template_path}")
        return
    
    prs = Presentation(str(template_path))
    
    # Insert each image as a slide (need template slides for duplication)
    for img in images:
        insert_image_slide(prs, str(img), caption)
    
    # Delete template slides after adding content
    delete_template_slides(prs)
    
    # Save the presentation
    prs.save(output)
    print(f"Saved presentation to {output}")
