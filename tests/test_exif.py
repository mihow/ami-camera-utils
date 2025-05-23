#!/usr/bin/env python3
"""
Test script to examine EXIF data from Entocam test images.
"""

import sys
import datetime
from pathlib import Path
import exifread

def print_exif_info(file_path):
    """Print relevant EXIF information from an image file."""
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f)
            
        print(f"File: {file_path}")
        print("="*50)
        
        # Look for datetime tags
        datetime_tags = [
            'EXIF DateTimeOriginal', 
            'EXIF DateTimeDigitized', 
            'Image DateTime'
        ]
        
        for tag_name in datetime_tags:
            if tag_name in tags:
                date_str = str(tags[tag_name])
                print(f"{tag_name}: {date_str}")
                # Parse the datetime
                dt = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                print(f"Parsed datetime: {dt}")
                # What it should be (May 16/17, 2025)
                print(f"Expected month/day: May 16/17, 2025")
                
        # List all tags with 'date' or 'time' in their name for reference
        print("\nAll date/time related tags:")
        for tag, value in tags.items():
            if 'date' in tag.lower() or 'time' in tag.lower():
                print(f"{tag}: {value}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Use the first image in the Entocam test folder
    test_image = Path("Entocam test 2025-05-17/DSCF0988.JPG")
    
    if not test_image.exists():
        print(f"Test image not found: {test_image}")
        sys.exit(1)
        
    print_exif_info(test_image)
