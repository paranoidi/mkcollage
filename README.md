# MkCollage

A simple command-line tool for creating grid collages from a folder of images. Automatically determines the most common aspect ratio from your images and preserves all original image content without cropping.

## Installation

Install using [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
uv tool install mkcollage
```

Git checkout (development):

```bash
uv sync
```

## Usage

Basic usage (auto-detects aspect ratio, outputs to current directory with folder name):

```bash
mkcollage /path/to/images
# Creates: ./images.jpg
```

Specify output filename:

```bash
mkcollage /path/to/images mycollage
# Creates: ./mycollage.jpg (in current directory)
```

Specify full output path:

```bash
mkcollage /path/to/images /output/path/collage.jpg
# Creates: /output/path/collage.jpg
```

With custom options:

```bash
mkcollage /path/to/images output.jpg \
  --size 2560 \
  --padding 20 \
  --centered \
  --background "#000000" \
  --quality 80
```

Specify exact dimensions:

```bash
mkcollage /path/to/images output.jpg \
  --width 1920 \
  --height 1080
```

Add a title to the collage:

```bash
mkcollage /path/to/images output.jpg \
  --title "My Photo Collection" \
  --title-size 64 \
  --title-color "#FFFFFF" \
  --title-border 3 \
  --title-border-color "#000000"
```

Use custom font for title:

```bash
mkcollage /path/to/images output.jpg \
  --title "Vacation 2025" \
  --title-font /path/to/font.ttf \
  --title-size 72
```

Reserve space for title (instead of drawing over collage):

```bash
mkcollage /path/to/images output.jpg \
  --title "My Collection" \
  --title-margin
```

### Command-line Options

- `folder` - Path to folder containing images (required)
- `output` - Output filename (optional, defaults to folder name). If no path is given, saves to current directory. Extension defaults to .jpg if not provided.
- `--size` - Target size for the larger dimension of the collage (default: 1920)
- `--width` - Width of the output collage (overrides --size and auto aspect ratio)
- `--height` - Height of the output collage (overrides --size and auto aspect ratio)
- `--padding` - Padding between images in pixels (default: 5)
- `--columns` - Number of images per row. If not specified, automatically calculates a square-ish grid. Useful for many images to keep them larger and make the collage taller.
- `--max-rows` - Maximum number of rows. If there are too many images to fit, a sample will be created that always includes the first and last images. A "Sample N of M" label will be shown in the top-right corner.
- `--background` - Background color in hex format (default: #000000)
- `--quality` - JPEG quality (1-100, default: 80)
- `--title` - Title text to add to top-left corner (optional)
- `--title-size` - Title font size in pixels (default: 24)
- `--title-font` - Path to TTF font file (uses system default if not specified)
- `--title-color` - Title text color in hex format (default: #FFFFFF)
- `--title-border` - Title text border/stroke width in pixels (default: 2)
- `--title-border-color` - Title text border color in hex format (default: #000000)
- `--title-margin` - Reserve space at the top for the title instead of drawing over the collage

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
- **Optional title text** - Add customizable title with font, size, color, and border options
- **Customizable** - Adjust padding, centering, background color, and JPEG quality

## How It Works

1. Scans the specified folder for all image files
2. Analyzes the aspect ratios of random 20 images
3. Determines the most common aspect ratio (e.g., 16:9, 4:3)
4. Calculates optimal canvas dimensions based on that ratio
5. Creates a grid layout that fits all images
6. Resizes each image to fit its grid cell while preserving aspect ratio
7. Adds letterboxing/pillarboxing with the background color as needed
8. Saves the final collage

## Requirements

- Python >= 3.8
- Pillow >= 10.0.0

