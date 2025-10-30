# Collage

A simple command-line tool for creating grid collages from a folder of images. Automatically determines the most common aspect ratio from your images and preserves all original image content without cropping.

## Installation

Install using `uv`:

```bash
uv pip install .
```

Or for development:

```bash
uv pip install -e .
```

## Usage

Basic usage (auto-detects aspect ratio, outputs to current directory with folder name):

```bash
collage /path/to/images
# Creates: ./images.jpg
```

Specify output filename:

```bash
collage /path/to/images mycollage
# Creates: ./mycollage.jpg (in current directory)
```

Specify full output path:

```bash
collage /path/to/images /output/path/collage.jpg
# Creates: /output/path/collage.jpg
```

With custom options:

```bash
collage /path/to/images output.jpg \
  --size 2560 \
  --padding 20 \
  --centered \
  --background "#000000" \
  --quality 95
```

Specify exact dimensions:

```bash
collage /path/to/images output.jpg \
  --width 1920 \
  --height 1080
```

### Command-line Options

- `folder` - Path to folder containing images (required)
- `output` - Output filename (optional, defaults to folder name). If no path is given, saves to current directory. Extension defaults to .jpg if not provided.
- `--size` - Target size for the larger dimension of the collage (default: 1920)
- `--width` - Width of the output collage (overrides --size and auto aspect ratio)
- `--height` - Height of the output collage (overrides --size and auto aspect ratio)
- `--padding` - Padding between images in pixels (default: 10)
- `--centered` - Center the grid if canvas is not square
- `--background` - Background color in hex format (default: #000000)
- `--quality` - JPEG quality (1-100, default: 80)

### Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

## Features

- **Automatic aspect ratio detection** - Analyzes all images and uses the most common aspect ratio
- **Preserves original content** - No cropping! Images are resized to fit while maintaining their aspect ratio
- **Smart letterboxing** - Adds background color bars when needed to fit images in grid cells
- **Grid layout optimization** - Automatically arranges images based on the canvas dimensions
- **Sorted processing** - Images are processed in alphabetical order
- **Flexible sizing** - Auto-calculate dimensions or specify exact width/height
- **Customizable** - Adjust padding, centering, and background color

## How It Works

1. Scans the specified folder for all image files
2. Analyzes the aspect ratios of all images
3. Determines the most common aspect ratio (e.g., 16:9, 4:3)
4. Calculates optimal canvas dimensions based on that ratio
5. Creates a grid layout that fits all images
6. Resizes each image to fit its grid cell while preserving aspect ratio
7. Adds letterboxing/pillarboxing with the background color as needed
8. Saves the final collage

## Requirements

- Python >= 3.8
- Pillow >= 10.0.0

