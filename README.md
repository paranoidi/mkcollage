# Collage

A simple command-line tool for creating grid collages from a folder of images.

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

Basic usage:

```bash
collage /path/to/images output.png
```

With custom options:

```bash
collage /path/to/images output.png \
  --width 2560 \
  --height 1440 \
  --padding 20 \
  --centered \
  --background "#000000"
```

### Command-line Options

- `folder` - Path to folder containing images (required)
- `output` - Output filename with path (required)
- `--width` - Width of the output collage in pixels (default: 1920)
- `--height` - Height of the output collage in pixels (default: 1080)
- `--padding` - Padding between images in pixels (default: 10)
- `--centered` - Center the grid if canvas is not square
- `--background` - Background color in hex format (default: #FFFFFF)

### Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

## Features

- Automatically discovers all images in a specified folder
- Creates a grid layout optimized for the canvas dimensions
- Processes images in sorted order (alphabetically)
- Resizes and crops images to fit the grid cells
- Customizable canvas size, padding, and background color

## Requirements

- Python >= 3.8
- Pillow >= 10.0.0

