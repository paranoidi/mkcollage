import argparse
import math
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageOps


def get_aspect_ratio(img_path):
    """Get the aspect ratio of an image."""
    with Image.open(img_path) as img:
        return img.width / img.height


def determine_common_aspect_ratio(image_files):
    """
    Determine the most common aspect ratio from a list of images.
    
    Returns:
        tuple: (width_ratio, height_ratio, actual_ratio_float)
    """
    aspect_ratios = []
    
    for img_path in image_files:
        ratio = get_aspect_ratio(img_path)
        # Round to 2 decimal places to group similar ratios
        aspect_ratios.append(round(ratio, 2))
    
    # Find most common aspect ratio
    counter = Counter(aspect_ratios)
    most_common_ratio = counter.most_common(1)[0][0]
    
    print(f"Most common aspect ratio: {most_common_ratio:.2f}:1")
    
    # Convert to simple ratio (e.g., 16:9, 4:3, etc.)
    # Common ratios
    common_ratios = {
        1.33: (4, 3),
        1.78: (16, 9),
        1.77: (16, 9),
        1.60: (16, 10),
        1.50: (3, 2),
        1.00: (1, 1),
        0.75: (3, 4),
        0.67: (2, 3),
        0.56: (9, 16),
    }
    
    # Find closest common ratio
    closest_ratio = min(common_ratios.keys(), key=lambda x: abs(x - most_common_ratio))
    if abs(closest_ratio - most_common_ratio) < 0.1:
        width_ratio, height_ratio = common_ratios[closest_ratio]
        print(f"Using standard aspect ratio: {width_ratio}:{height_ratio}")
    else:
        # Use the actual ratio
        width_ratio, height_ratio = most_common_ratio, 1.0
        print(f"Using custom aspect ratio: {most_common_ratio:.2f}:1")
    
    return width_ratio, height_ratio, most_common_ratio


def fit_image_preserve_aspect(img, cell_width, cell_height, background_color):
    """
    Resize image to fit within cell while preserving aspect ratio.
    Adds letterboxing/pillarboxing if needed.
    """
    # Calculate the scaling factor to fit the image in the cell
    img_ratio = img.width / img.height
    cell_ratio = cell_width / cell_height
    
    if img_ratio > cell_ratio:
        # Image is wider than cell - fit to width
        new_width = cell_width
        new_height = int(cell_width / img_ratio)
    else:
        # Image is taller than cell - fit to height
        new_height = cell_height
        new_width = int(cell_height * img_ratio)
    
    # Resize the image
    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create a new image with the cell size and background color
    result = Image.new('RGB', (cell_width, cell_height), background_color)
    
    # Paste the resized image in the center
    x_offset = (cell_width - new_width) // 2
    y_offset = (cell_height - new_height) // 2
    result.paste(img_resized, (x_offset, y_offset))
    
    return result


def grid_collage(images, collage, padding, centered, background_color):
    """
    Create a grid-based collage that preserves original image aspect ratios.

    Parameters:
        images (list): List of image file paths to include in the collage.
        collage (PIL.Image): Blank canvas to place the images.
        padding (int): Space between images and canvas edges.
        centered (bool): Whether to center the grid if the canvas is not square.
        background_color (str): Background color for letterboxing/pillarboxing.
    """
    images_num = len(images)
    canvas_width, canvas_height = collage.size
    
    # Determine grid dimensions
    cols = math.ceil(math.sqrt(images_num))
    rows = math.ceil(images_num / cols)
    offset_x, offset_y = 0, 0
    
    # Adjust grid dimensions based on canvas proportions
    canvas_ratio = canvas_width / canvas_height
    if canvas_ratio > 1:  # Landscape canvas
        if cols < rows:
            cols, rows = rows, cols
        if centered:
            total_width = cols * ((canvas_width - (cols + 1) * padding) // cols) + (cols + 1) * padding
            offset_x = (canvas_width - total_width) // 2
    elif canvas_ratio < 1:  # Portrait canvas
        if cols > rows:
            cols, rows = rows, cols
        if centered:
            total_height = rows * ((canvas_height - (rows + 1) * padding) // rows) + (rows + 1) * padding
            offset_y = (canvas_height - total_height) // 2
    
    # Calculate cell dimensions
    cell_width = (canvas_width - (cols + 1) * padding) // cols
    cell_height = (canvas_height - (rows + 1) * padding) // rows
    
    # Process each image
    for idx, img_path in enumerate(images):
        img = Image.open(img_path)
        
        # Fit image preserving aspect ratio
        fitted_img = fit_image_preserve_aspect(img, cell_width, cell_height, background_color)
        
        # Calculate position in the grid
        col = idx % cols
        row = idx // cols
        x = col * (cell_width + padding) + padding + offset_x
        y = row * (cell_height + padding) + padding + offset_y
        
        collage.paste(fitted_img, (x, y))
    
    return collage


def get_image_files(folder_path):
    """Get all image files from the specified folder."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        sys.exit(1)
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        sys.exit(1)
    
    image_files = []
    for file in sorted(folder.iterdir()):
        if file.is_file() and file.suffix.lower() in image_extensions:
            image_files.append(str(file))
    
    return image_files


def determine_output_path(output_arg, folder_path):
    """
    Determine the output file path based on user input.
    
    Args:
        output_arg: Output argument from command line (can be None)
        folder_path: Path to the folder containing images
        
    Returns:
        str: Full output file path
    """
    if output_arg is None:
        # Use the last directory name from folder path as output filename
        folder_path = Path(folder_path).resolve()
        output_name = folder_path.name + '.jpg'
        output_path = Path.cwd() / output_name
        print(f"No output specified, using: {output_path}")
    else:
        output_path = Path(output_arg)
        # If output has no directory component, use current directory
        if output_path.parent == Path('.'):
            output_path = Path.cwd() / output_path.name
        # Ensure .jpg extension if no extension provided
        if not output_path.suffix:
            output_path = output_path.with_suffix('.jpg')
    
    return str(output_path)


def calculate_canvas_dimensions(aspect_ratio, size=None, width=None, height=None):
    """
    Calculate canvas dimensions based on aspect ratio and user preferences.
    
    Args:
        aspect_ratio: The aspect ratio to use (width/height)
        size: Target size for the larger dimension
        width: Explicit width (overrides size)
        height: Explicit height (overrides size)
        
    Returns:
        tuple: (canvas_width, canvas_height)
    """
    if width and height:
        # Both dimensions specified
        canvas_width, canvas_height = width, height
        print(f"Using specified dimensions: {canvas_width}x{canvas_height}")
    elif width:
        # Only width specified
        canvas_width = width
        canvas_height = int(canvas_width / aspect_ratio)
        print(f"Calculated dimensions from width: {canvas_width}x{canvas_height}")
    elif height:
        # Only height specified
        canvas_height = height
        canvas_width = int(canvas_height * aspect_ratio)
        print(f"Calculated dimensions from height: {canvas_width}x{canvas_height}")
    else:
        # Use aspect ratio with target size
        if aspect_ratio >= 1:
            # Landscape or square - size is width
            canvas_width = size
            canvas_height = int(canvas_width / aspect_ratio)
        else:
            # Portrait - size is height
            canvas_height = size
            canvas_width = int(canvas_height * aspect_ratio)
        print(f"Auto-calculated dimensions: {canvas_width}x{canvas_height}")
    
    return canvas_width, canvas_height


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Create a grid collage from images in a folder.'
    )
    parser.add_argument(
        'folder',
        type=str,
        help='Path to folder containing images'
    )
    parser.add_argument(
        'output',
        type=str,
        nargs='?',
        default=None,
        help='Output filename (optional, defaults to folder name). If no path is given, saves to current directory.'
    )
    parser.add_argument(
        '--size',
        type=int,
        default=1920,
        help='Target size for the larger dimension of the collage (default: 1920)'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=None,
        help='Width of the output collage (overrides --size and auto aspect ratio)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=None,
        help='Height of the output collage (overrides --size and auto aspect ratio)'
    )
    parser.add_argument(
        '--padding',
        type=int,
        default=10,
        help='Padding between images in pixels (default: 10)'
    )
    parser.add_argument(
        '--centered',
        action='store_true',
        help='Center the grid if canvas is not square'
    )
    parser.add_argument(
        '--background',
        type=str,
        default='#000000',
        help='Background color in hex format (default: #000000)'
    )
    parser.add_argument(
        '--quality',
        type=int,
        default=80,
        help='JPEG quality (1-100, default: 80)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the collage CLI."""
    args = parse_arguments()
    
    # Get image files from folder
    image_files = get_image_files(args.folder)
    
    if not image_files:
        print(f"Error: No image files found in '{args.folder}'.")
        sys.exit(1)
    
    print(f"Found {len(image_files)} images in '{args.folder}'")
    
    # Determine output path
    output_file = determine_output_path(args.output, args.folder)
    
    # Determine the most common aspect ratio
    width_ratio, height_ratio, aspect_ratio = determine_common_aspect_ratio(image_files)
    
    # Calculate canvas dimensions
    canvas_width, canvas_height = calculate_canvas_dimensions(
        aspect_ratio,
        size=args.size,
        width=args.width,
        height=args.height
    )
    
    # Create blank canvas
    collage = Image.new("RGB", (canvas_width, canvas_height), args.background)
    
    # Create the grid collage
    print(f"Creating grid collage...")
    collage = grid_collage(image_files, collage, args.padding, args.centered, args.background)
    
    # Save the collage
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    collage.save(output_file, quality=args.quality, optimize=True)
    
    print(f"Collage saved to: {output_file}")


if __name__ == "__main__":
    main()

