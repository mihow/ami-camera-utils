# Camera Test Utilities

This repository contains Python utilities for managing and processing camera test images.

## Photo Renamer

A Python utility that renames image files based on their EXIF timestamp data. It can recursively scan directories, apply date/time corrections, and show a preview before making changes.

## Photo Sampler

A companion utility that samples images at regular time intervals based on EXIF timestamps. It creates a subset of images by selecting one image per specified time interval, which is useful for time-lapse creation and long-term monitoring studies.

## Features

### Photo Renamer

- Extracts timestamp data from image EXIF metadata
- Renames files using the format: `prefix-YYYYMMDDHHmmSS.ext`
- Supports date/time correction for cameras with incorrect time settings
- Recursive directory scanning
- Dry run mode to preview changes before applying them
- Interactive confirmation before renaming files

### Photo Sampler

- Samples images at specified time intervals (default 10 minutes)
- Copies selected images to a target directory (default "snapshots")
- Preserves original files without modification
- Optional time correction for cameras with incorrect date settings
- Can preserve directory structure in the output
- Dry run mode to preview selection before copying

## Installation

```bash
# Make sure you have the required packages
poetry install
```

## Usage

### Photo Renamer

#### Basic Usage

```bash
poetry run photo-renamer "path/to/photos" --inplace
```

#### With Date Correction

```bash
# Add 1 year and 53 days to all timestamps (418 days total)
python photo_renamer.py "path/to/photos" --days 418

# Adjust by specific time units
python photo_renamer.py "path/to/photos" --days 365 --hours 12 --minutes 30
```

#### Preview Mode (Dry Run)

```bash
python photo_renamer.py "path/to/photos" --dry-run
```

#### Skip Confirmation Prompt

```bash
python photo_renamer.py "path/to/photos" --yes
```

#### Additional Options

```bash
# Change the filename prefix (default is "entocamtest")
python photo_renamer.py "path/to/photos" --prefix "vacation"

# Disable recursive scanning
python photo_renamer.py "path/to/photos" --no-recursive
```

### Photo Sampler

#### Basic Usage

```bash
# Sample at default 10-minute intervals
python photo_sampler.py "path/to/photos"
```

#### Custom Interval

```bash
# Sample at 30-minute intervals
python photo_sampler.py "path/to/photos" --interval 30
```

#### Custom Output Directory

```bash
# Save to a specific folder
python photo_sampler.py "path/to/photos" --output-dir "30min-samples"
```

#### With Date Correction

```bash
# Apply date correction to cameras with incorrect settings
python photo_sampler.py "path/to/photos" --days 418
```

#### Preserve Directory Structure

```bash
# Maintain the original folder hierarchy in the output
python photo_sampler.py "path/to/photos" --preserve-structure
```

#### Preview Mode (Dry Run)

```bash
# Show what would be done without copying files
python photo_sampler.py "path/to/photos" --dry-run
```

## Examples

### Photo Renamer Example

For the Entocam test 2025-05-17 folder (with incorrect dates of March 2024):

```bash
# Preview changes
python photo_renamer.py "Entocam test 2025-05-17" --days 418 --dry-run

# Apply the changes
python photo_renamer.py "Entocam test 2025-05-17" --days 418
```

### Photo Sampler Example

To create a time-lapse sequence from the same folder:

```bash
# Sample at 30-minute intervals with preview
python photo_sampler.py "Entocam test 2025-05-17" --interval 30 --days 418 --dry-run

# Execute the sampling
python photo_sampler.py "Entocam test 2025-05-17" --interval 30 --days 418 --output-dir "timelapse-30min"
```

## Full Command-line Reference

### Photo Renamer

```
Usage: photo_renamer.py [OPTIONS] DIRECTORY

  Rename image files based on their EXIF timestamp.

  This utility processes images from the specified directory and renames them
  according to their EXIF timestamp (with optional correction), following the
  format: prefix-YYYYMMDDHHmmSS.ext

Arguments:
  DIRECTORY  Directory containing images to rename  [required]

Options:
  -d, --days INTEGER              Days to add to the timestamp (can be negative)
  -h, --hours INTEGER             Hours to add to the timestamp (can be negative)
  -m, --minutes INTEGER           Minutes to add to the timestamp (can be negative)
  -r, --recursive / -nr, --no-recursive
                                  Whether to search recursively  [default: True]
  -p, --prefix TEXT               Prefix for the new filenames  [default: entocamtest]
  -n, --dry-run                   Show what would be done without actually renaming files
  -y, --yes                       Skip confirmation prompt and proceed with renaming
  --help                          Show this message and exit.
```

### Photo Sampler

```
Usage: photo_sampler.py [OPTIONS] DIRECTORY

  Sample image files at specific time intervals based on their EXIF timestamp.

  This utility processes images from the specified directory and selects one image
  per time interval based on the EXIF timestamp. The selected images are copied to
  the output directory.

Arguments:
  DIRECTORY  Directory containing images to sample  [required]

Options:
  -o, --output-dir PATH           Directory to save sampled images  [default: snapshots]
  -i, --interval INTEGER          Sampling interval in minutes  [default: 10]
  -d, --days INTEGER              Days to add to the timestamp (can be negative)
  -h, --hours INTEGER             Hours to add to the timestamp (can be negative)
  -m, --minutes INTEGER           Minutes to add to the timestamp (can be negative)
  -r, --recursive / -nr, --no-recursive
                                  Whether to search recursively  [default: True]
  -p, --preserve-structure        Preserve directory structure in output
  -n, --dry-run                   Show what would be done without actually copying files
  -y, --yes                       Skip confirmation prompt and proceed with copying
  --help                          Show this message and exit.
```

## Included Test Scripts

### test_exif.py

A simple script to examine the EXIF data in a sample image:

```bash
python test_exif.py
```

### test_renaming.py

Shows a preview of the renaming process and helps calculate the appropriate date offset:

```bash
python test_renaming.py
```

### test_sampling.py

Demonstrates how to use the photo sampling utility with example commands:

```bash
python test_sampling.py
