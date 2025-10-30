"""Text rendering and visual overlay utilities."""

from PIL import Image, ImageDraw, ImageFont


def load_font(font_path, font_size):
    """
    Load a font for text rendering.
    
    Args:
        font_path: Path to TTF font file (None for default)
        font_size: Size of the font in pixels
        
    Returns:
        PIL ImageFont object
    """
    try:
        if font_path:
            return ImageFont.truetype(font_path, font_size)
        else:
            # Try to use a default system font
            try:
                # Try common system fonts
                for font_name in [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                    "C:\\Windows\\Fonts\\arial.ttf",
                ]:
                    try:
                        return ImageFont.truetype(font_name, font_size)
                    except:
                        continue
                else:
                    # Fall back to default font
                    print("Warning: Using default font. Specify --title-font for better results.")
                    return ImageFont.load_default()
            except:
                print("Warning: Using default font. Specify --title-font for better results.")
                return ImageFont.load_default()
    except Exception as e:
        print(f"Warning: Could not load font: {e}. Using default font.")
        return ImageFont.load_default()


def calculate_title_space(title, font_size, font_path, border_width):
    """
    Calculate the vertical space needed for the title.
    
    Args:
        title: Text to display
        font_size: Size of the font in pixels
        font_path: Path to TTF font file (None for default)
        border_width: Width of the text border/stroke
        
    Returns:
        int: Height in pixels needed for the title
    """
    font = load_font(font_path, font_size)
    
    # Create a temporary draw object to measure text
    temp_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(temp_img)
    
    # Get bounding box of the text
    bbox = draw.textbbox((0, 0), title, font=font)
    text_height = bbox[3] - bbox[1]
    
    # Add padding (20px top + 20px bottom) and border space
    padding = 20
    total_height = text_height + (2 * padding) + (2 * border_width)
    
    return int(total_height)


def create_canvas_with_title_space(canvas_width, canvas_height, background_color, 
                                   title_space_height):
    """
    Create a canvas with extra space at the top for the title.
    
    Args:
        canvas_width: Width of the main collage area
        canvas_height: Height of the main collage area
        background_color: Background color
        title_space_height: Extra height for title at the top
        
    Returns:
        tuple: (full_canvas, collage_canvas, title_offset_y)
    """
    # Create full canvas with extra space at top
    full_height = canvas_height + title_space_height
    full_canvas = Image.new("RGB", (canvas_width, full_height), background_color)
    
    # Create a canvas for the collage part (without title space)
    collage_canvas = Image.new("RGB", (canvas_width, canvas_height), background_color)
    
    return full_canvas, collage_canvas, title_space_height


def add_title_to_collage(image, title, font_size=48, font_path=None, text_color='#FFFFFF', 
                         border_width=2, border_color='#000000', position='top-left'):
    """
    Add title text to the collage with a border.
    
    Args:
        image: PIL Image object
        title: Text to display
        font_size: Size of the font in pixels
        font_path: Path to TTF font file (None for default)
        text_color: Color of the text in hex format
        border_width: Width of the text border/stroke
        border_color: Color of the border in hex format
        position: Text position - 'top-left' or 'top-right'
        
    Returns:
        PIL Image object with title added
    """
    draw = ImageDraw.Draw(image)
    font = load_font(font_path, font_size)
    
    # Calculate text position with padding from edges
    padding = 20
    
    # Get text bounding box for width calculation
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    
    # Calculate x position based on alignment
    if position == 'top-right':
        x = image.width - text_width - padding - (2 * border_width)
    else:  # top-left (default)
        x = padding
    
    y = padding
    
    # Draw text with border (by drawing the text multiple times with offset)
    if border_width > 0:
        # Draw border by drawing text in all directions
        for offset_x in range(-border_width, border_width + 1):
            for offset_y in range(-border_width, border_width + 1):
                if offset_x != 0 or offset_y != 0:
                    draw.text((x + offset_x, y + offset_y), title, font=font, fill=border_color)
    
    # Draw the main text
    draw.text((x, y), title, font=font, fill=text_color)
    
    return image


def setup_canvas_with_title(canvas_width, canvas_height, background_color, 
                            title_text=None, title_margin=False, 
                            title_size=48, title_font=None, title_border=2):
    """
    Setup canvas with optional title space.
    
    Args:
        canvas_width: Width of the collage area
        canvas_height: Height of the collage area
        background_color: Background color
        title_text: Title text (None if no title)
        title_margin: Whether to reserve space for title
        title_size: Font size for title
        title_font: Path to font file
        title_border: Border width for title
        
    Returns:
        tuple: (final_canvas, collage_canvas, title_offset)
    """
    title_space_height = 0
    
    # Calculate title space if needed
    if title_text and title_margin:
        title_space_height = calculate_title_space(
            title_text,
            title_size,
            title_font,
            title_border
        )
        print(f"Reserving {title_space_height}px space for title")
    
    # Create canvas(es)
    if title_space_height > 0:
        # Create canvas with extra space for title
        final_canvas, collage_canvas, title_offset = create_canvas_with_title_space(
            canvas_width, canvas_height, background_color, title_space_height
        )
    else:
        # Create single canvas
        collage_canvas = Image.new("RGB", (canvas_width, canvas_height), background_color)
        final_canvas = collage_canvas
        title_offset = 0
    
    return final_canvas, collage_canvas, title_offset


def apply_title_to_collage(collage, title_text, title_size, title_font,
                           title_color, title_border, title_border_color):
    """
    Apply title text to the collage if specified.
    
    Returns:
        PIL.Image: Collage with title applied
    """
    if not title_text:
        return collage
    
    print(f"Adding title: {title_text}")
    return add_title_to_collage(
        collage,
        title_text,
        font_size=title_size,
        font_path=title_font,
        text_color=title_color,
        border_width=title_border,
        border_color=title_border_color,
        position='top-left'
    )


def apply_sample_label(collage, is_sampled, sample_count, total_count,
                       title_size, title_font, title_color, 
                       title_border, title_border_color):
    """
    Apply sample label to the collage if images were sampled.
    
    Returns:
        PIL.Image: Collage with sample label applied
    """
    if not is_sampled:
        return collage
    
    sample_text = f"Sample {sample_count} of {total_count}"
    print(f"Adding sample label: {sample_text}")
    return add_title_to_collage(
        collage,
        sample_text,
        font_size=title_size,
        font_path=title_font,
        text_color=title_color,
        border_width=title_border,
        border_color=title_border_color,
        position='top-right'
    )

