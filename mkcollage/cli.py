"""Command-line interface for the collage generator."""

import argparse
import sys
from pathlib import Path

from .image_ops import (
    apply_image_sampling,
    determine_common_aspect_ratio,
    determine_output_path,
    get_image_files,
)
from .layout import (
    calculate_grid_layout,
    create_collage_canvas,
)
from .rendering import apply_sample_label, apply_title_to_collage


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
        default=5,
        help='Padding between images in pixels (default: 5)'
    )
    parser.add_argument(
        '--columns',
        type=int,
        default=None,
        help='Number of images per row. If not specified, automatically calculates a square-ish grid. Useful for many images to keep them larger and make the collage taller.'
    )
    parser.add_argument(
        '--max-rows',
        type=int,
        default=None,
        help='Maximum number of rows. If there are too many images to fit, a sample will be created that always includes the first and last images. A "Sample N of M" label will be shown in the top-right corner.'
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
    parser.add_argument(
        '--title',
        type=str,
        default=None,
        help='Title text to add to top-left corner'
    )
    parser.add_argument(
        '--title-size',
        type=int,
        default=24,
        help='Title font size in pixels (default: 24)'
    )
    parser.add_argument(
        '--title-font',
        type=str,
        default=None,
        help='Path to TTF font file (uses default if not specified)'
    )
    parser.add_argument(
        '--title-color',
        type=str,
        default='#FFFFFF',
        help='Title text color in hex format (default: #FFFFFF)'
    )
    parser.add_argument(
        '--title-border',
        type=int,
        default=2,
        help='Title text border/stroke width in pixels (default: 2)'
    )
    parser.add_argument(
        '--title-border-color',
        type=str,
        default='#000000',
        help='Title text border color in hex format (default: #000000)'
    )
    parser.add_argument(
        '--title-margin',
        action='store_true',
        help='Reserve space at the top for the title instead of drawing over the collage'
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
    
    # Apply sampling if max-rows is specified
    image_files, is_sampled, total_image_count = apply_image_sampling(
        image_files, args.columns, args.max_rows
    )
    
    # Determine output path
    output_file = determine_output_path(args.output, args.folder)
    
    # Determine the most common aspect ratio
    width_ratio, height_ratio, aspect_ratio = determine_common_aspect_ratio(image_files)
    
    # Calculate complete grid layout (single source of truth)
    layout = calculate_grid_layout(
        num_images=len(image_files),
        aspect_ratio=aspect_ratio,
        padding=args.padding,
        size=args.size,
        width=args.width,
        height=args.height,
        columns=args.columns,
        max_rows=args.max_rows
    )
    
    # Create the collage canvas and grid
    collage = create_collage_canvas(
        image_files, layout, args.background,
        args.title, args.title_margin, args.title_size,
        args.title_font, args.title_border
    )
    
    # Apply title text
    collage = apply_title_to_collage(
        collage, args.title, args.title_size, args.title_font,
        args.title_color, args.title_border, args.title_border_color
    )
    
    # Apply sample label if needed
    collage = apply_sample_label(
        collage, is_sampled, len(image_files), total_image_count,
        args.title_size, args.title_font, args.title_color,
        args.title_border, args.title_border_color
    )
    
    # Save the collage
    print("Saving collage...")
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    collage.save(output_file, quality=args.quality, optimize=True)
    
    print(f"Collage saved to: {output_file}")


if __name__ == "__main__":
    main()
