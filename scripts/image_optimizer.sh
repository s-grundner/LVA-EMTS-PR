#!/bin/zsh

# interactive image optimizer for LaTeX projects
# requires ImageMagick (install with: brew install imagemagick)

# --- check input ---
if [ -z "$1" ]; then
    echo "Usage: '$0' <basepath>"
    echo "  <basepath> = directory that contains 'images/'"
    exit 1
fi

BASEPATH="$1"
IMGDIR="$BASEPATH/images"
OUTDIR="$BASEPATH/images_optimized"

if [ ! -d "$IMGDIR" ]; then
    echo "Error: '$IMGDIR' does not exist."
    exit 1
fi

# --- ask user interactively ---
read -p "Target max width in px [default 1600]: " WIDTH
WIDTH=${WIDTH:-1600}

read -p "JPEG quality (1–100) [default 82]: " QUALITY
QUALITY=${QUALITY:-82}

echo "Optimizing images from $IMGDIR → $OUTDIR"
mkdir -p "$OUTDIR"

# set case-insensitive
setopt nocaseglob

# --- process JPG ---
echo "Processing JPGs..."
mogrify -path "$OUTDIR" -resize "${WIDTH}x" -quality "$QUALITY" -strip "$IMGDIR"/*.{jpg,jpeg} 2>/dev/null

# --- process PNG ---
echo "Processing PNGs..."
mogrify -path "$OUTDIR" -resize "${WIDTH}x" -strip "$IMGDIR"/*.png 2>/dev/null

echo "Done. Optimized images are in: $OUTDIR"
