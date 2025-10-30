"""Image operations and analysis utilities."""

import random
import sys
from collections import Counter
from pathlib import Path

from PIL import Image


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


def get_aspect_ratio(img_path):
    """Get the aspect ratio of an image."""
    try:
        with Image.open(img_path) as img:
            return img.width / img.height
    except Exception as e:
        # Return None if the file cannot be opened as an image
        return None


def determine_common_aspect_ratio(image_files):
    """
    Determine the most common aspect ratio from a list of images.
    Samples 20 images randomly for efficiency.
    
    Returns:
        tuple: (width_ratio, height_ratio, actual_ratio_float)
    """
    # Sample images for aspect ratio analysis
    total_images = len(image_files)
    sample_size = 20
    
    if total_images > sample_size:
        sampled_files = random.sample(image_files, sample_size)
        print(f"Analyzing aspect ratio from {sample_size} randomly sampled images...")
    else:
        sampled_files = image_files
        print(f"Analyzing aspect ratio from all {total_images} images...")
    
    aspect_ratios = []
    
    for idx, img_path in enumerate(sampled_files):
        # Show progress
        progress = idx + 1
        total = len(sampled_files)
        sys.stdout.write(f"\rAnalyzing images: {progress}/{total} ({100 * progress // total}%)")
        sys.stdout.flush()
        
        ratio = get_aspect_ratio(img_path)
        if ratio is None:
            print(f"\nWarning: Skipping '{img_path}' - not a valid image file")
            continue
        # Round to 2 decimal places to group similar ratios
        aspect_ratios.append(round(ratio, 2))
    
    # Complete the progress line
    sys.stdout.write("\n")
    sys.stdout.flush()
    
    # Check if we have any valid images
    if not aspect_ratios:
        print("Error: No valid images found in the folder.")
        sys.exit(1)
    
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


def sample_images(image_files, max_count):
    """
    Sample images from the list, always including first and last.
    
    Args:
        image_files: List of image file paths
        max_count: Maximum number of images to include
        
    Returns:
        list: Sampled list of image files
    """
    if len(image_files) <= max_count:
        return image_files
    
    if max_count < 2:
        return image_files[:max_count]
    
    # Always include first and last
    sampled = [image_files[0]]
    
    # Calculate indices for middle samples
    if max_count > 2:
        # We need to pick (max_count - 2) images from the middle
        remaining_slots = max_count - 2
        total_middle = len(image_files) - 2
        
        # Use evenly spaced indices
        step = total_middle / remaining_slots
        for i in range(remaining_slots):
            idx = int(1 + i * step + step / 2)  # +1 to skip first, center within step
            if idx < len(image_files) - 1:  # Don't go to last (we'll add it separately)
                sampled.append(image_files[idx])
    
    # Always include last
    sampled.append(image_files[-1])
    
    return sampled


def apply_image_sampling(image_files, columns, max_rows):
    """
    Apply image sampling if max-rows is specified.
    
    Args:
        image_files: List of image file paths
        columns: Number of columns
        max_rows: Maximum number of rows (None if not specified)
        
    Returns:
        tuple: (sampled_image_files, is_sampled, total_count)
    """
    total_image_count = len(image_files)
    is_sampled = False
    
    if max_rows and columns:
        max_images = columns * max_rows
        if len(image_files) > max_images:
            print(f"Sampling {max_images} images from {total_image_count} total (max-rows={max_rows}, columns={columns})")
            image_files = sample_images(image_files, max_images)
            is_sampled = True
            print(f"Selected images: {len(image_files)} (including first and last)")
    elif max_rows and not columns:
        print("Warning: --max-rows requires --columns to be specified. Ignoring --max-rows.")
    
    return image_files, is_sampled, total_image_count


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

