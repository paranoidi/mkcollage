"""Layout engine and canvas assembly."""

import math
import sys
from dataclasses import dataclass

from PIL import Image

from .image_ops import fit_image_preserve_aspect
from .rendering import setup_canvas_with_title


@dataclass
class GridLayout:
    """Contains all calculated grid layout parameters."""
    canvas_width: int
    canvas_height: int
    cols: int
    rows: int
    cell_width: int
    cell_height: int
    padding: int
    offset_x: int = 0
    offset_y: int = 0


def calculate_grid_layout(num_images, aspect_ratio, padding, 
                          size=None, width=None, height=None,
                          columns=None, max_rows=None):
    """
    Calculate complete grid layout with all parameters.
    
    This is the single source of truth for all grid calculations.
    
    Args:
        num_images: Number of images to display
        aspect_ratio: The aspect ratio of images (width/height)
        padding: Padding between images in pixels
        size: Target size for the larger dimension (default: 1920)
        width: Explicit width (overrides size)
        height: Explicit height (overrides size)
        columns: Number of columns (None for auto-calculate)
        max_rows: Maximum number of rows (None for unlimited)
        
    Returns:
        GridLayout: Object containing all calculated layout parameters
    """
    if size is None:
        size = 1920
    
    # Step 1: Determine grid dimensions (cols x rows)
    if columns:
        cols = columns
        if max_rows:
            rows = min(max_rows, math.ceil(num_images / cols))
        else:
            rows = math.ceil(num_images / cols)
    else:
        # Auto-calculate grid dimensions
        cols = math.ceil(math.sqrt(num_images))
        rows = math.ceil(num_images / cols)
    
    # Step 2: Calculate initial canvas dimensions
    if width and height:
        # Both dimensions specified by user
        canvas_width, canvas_height = width, height
        print(f"Using specified dimensions: {canvas_width}x{canvas_height}")
    elif width:
        # Only width specified - calculate height to fit grid
        canvas_width = width
        # Calculate cell dimensions from width
        cell_width = (canvas_width - (cols + 1) * padding) // cols
        cell_height = int(cell_width / aspect_ratio)
        # Calculate required height for grid
        canvas_height = rows * cell_height + (rows + 1) * padding
        print(f"Calculated dimensions from width: {canvas_width}x{canvas_height}")
    elif height:
        # Only height specified - calculate width to fit grid
        canvas_height = height
        # Calculate cell dimensions from height
        cell_height = (canvas_height - (rows + 1) * padding) // rows
        cell_width = int(cell_height * aspect_ratio)
        # Calculate required width for grid
        canvas_width = cols * cell_width + (cols + 1) * padding
        print(f"Calculated dimensions from height: {canvas_width}x{canvas_height}")
    else:
        # Auto-calculate dimensions based on size and grid layout
        # Adjust cols/rows based on canvas proportions
        if not columns:
            # Calculate grid aspect ratio
            grid_aspect_ratio = (cols / rows) * aspect_ratio
            
            # Adjust cols/rows to match grid aspect ratio better
            if grid_aspect_ratio > 1 and cols < rows:
                cols, rows = rows, cols
            elif grid_aspect_ratio < 1 and cols > rows:
                cols, rows = rows, cols
            
            # Recalculate grid aspect ratio after potential swap
            grid_aspect_ratio = (cols / rows) * aspect_ratio
            
            # Calculate canvas dimensions from size and grid aspect ratio
            if grid_aspect_ratio >= 1:
                canvas_width = size
                canvas_height = int(size / grid_aspect_ratio)
            else:
                canvas_height = size
                canvas_width = int(size * grid_aspect_ratio)
        else:
            # With explicit columns, use simple dimension calculation
            if aspect_ratio >= 1:
                canvas_width = size
                canvas_height = int(canvas_width / aspect_ratio)
            else:
                canvas_height = size
                canvas_width = int(canvas_height * aspect_ratio)
        
        print(f"Auto-calculated dimensions: {canvas_width}x{canvas_height}")
    
    # Step 3: Calculate cell dimensions
    # Always calculate cell_height from cell_width and aspect_ratio for consistency
    cell_width = (canvas_width - (cols + 1) * padding) // cols
    cell_height = int(cell_width / aspect_ratio)
    
    # Step 4: Adjust canvas height to exactly fit the grid (prevents extra space)
    # unless user explicitly set height
    if not height:
        canvas_height = rows * cell_height + (rows + 1) * padding
    
    # Step 5: Calculate offsets for centering (if auto-calculating layout)
    offset_x, offset_y = 0, 0
    if not columns and not width and not height:
        # For auto-calculated layouts, we might want to center
        # This is mainly for edge cases where canvas doesn't perfectly match grid
        pass  # Currently not needed with exact calculations
    
    print(f"Grid layout: {rows} rows × {cols} columns, cells: {cell_width}x{cell_height}px")
    
    return GridLayout(
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        cols=cols,
        rows=rows,
        cell_width=cell_width,
        cell_height=cell_height,
        padding=padding,
        offset_x=offset_x,
        offset_y=offset_y
    )


def grid_collage(images, collage, layout, background_color):
    """
    Create a grid-based collage using pre-calculated layout parameters.

    Parameters:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        layout (GridLayout): Pre-calculated grid layout parameters.
        background_color (str): Background color for letterboxing/pillarboxing.
    """
    # Process each image using pre-calculated layout values
    for idx, img_path in enumerate(images):
        # Show progress
        progress = idx + 1
        total = len(images)
        sys.stdout.write(f"\rProcessing images: {progress}/{total} ({100 * progress // total}%)")
        sys.stdout.flush()
        
        try:
            img = Image.open(img_path)
            
            # Fit image preserving aspect ratio
            fitted_img = fit_image_preserve_aspect(
                img, layout.cell_width, layout.cell_height, background_color
            )
            
            # Calculate position in the grid
            col = idx % layout.cols
            row = idx // layout.cols
            x = col * (layout.cell_width + layout.padding) + layout.padding + layout.offset_x
            y = row * (layout.cell_height + layout.padding) + layout.padding + layout.offset_y
            
            collage.paste(fitted_img, (x, y))
        except Exception as e:
            print(f"\nWarning: Skipping '{img_path}' - cannot open image: {e}")
            continue
    
    # Complete the progress line
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    return collage


def create_collage_canvas(image_files, layout, background_color,
                          title_text, title_margin, title_size, 
                          title_font, title_border):
    """
    Create the collage canvas and generate the grid collage.
    
    Args:
        image_files: List of image file paths
        layout: GridLayout object with all calculated parameters
        background_color: Background color for the canvas
        title_text: Title text (None if no title)
        title_margin: Whether to reserve space for title
        title_size: Font size for title
        title_font: Path to font file
        title_border: Border width for title
    
    Returns:
        PIL.Image: The completed collage canvas
    """
    # Setup canvas with optional title space
    final_canvas, collage_canvas, title_offset = setup_canvas_with_title(
        layout.canvas_width,
        layout.canvas_height,
        background_color,
        title_text=title_text,
        title_margin=title_margin,
        title_size=title_size,
        title_font=title_font,
        title_border=title_border
    )
    
    # Create the grid collage
    print(f"Creating grid collage...")
    collage_canvas = grid_collage(image_files, collage_canvas, layout, background_color)
    
    # If we reserved space, paste the collage onto the final canvas
    if title_offset > 0:
        final_canvas.paste(collage_canvas, (0, title_offset))
        return final_canvas
    else:
        return collage_canvas

