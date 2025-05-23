#!/usr/bin/env python3
"""
Test script to demonstrate photo renaming with correct date offset
"""

import os
from pathlib import Path
import datetime
import exifread


def get_exif_datetime(file_path):
    """Extract datetime from EXIF data"""
    with open(file_path, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        
    for tag in ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime']:
        if tag in tags:
            date_str = str(tags[tag])
            return datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
    return None


def calculate_offset():
    """Calculate required offset to correct dates"""
    # Original date in EXIF (wrong): March 24, 2024
    # Target date (correct): May 16-17, 2025
    
    # Calculate days between Mar 24, 2024 and May 16, 2025
    original_date = datetime.datetime(2024, 3, 24)
    target_date = datetime.datetime(2025, 5, 16)
    
    delta = target_date - original_date
    days = delta.days
    
    print(f"Days between Mar 24, 2024 and May 16, 2025: {days} days")
    print(f"This equals approximately {days//365} year and {days%365} days")
    
    return days


def generate_new_filename(original_path, timestamp, prefix="entocamtest"):
    """Generate new filename with date format"""
    time_str = timestamp.strftime("%Y%m%d%H%M%S")
    extension = original_path.suffix.lower()
    return f"{prefix}-{time_str}{extension}"


def test_rename_preview():
    """Preview what the renaming would look like"""
    test_dir = Path("Entocam test 2025-05-17")
    offset_days = calculate_offset()
    
    # Just process a few images as an example
    test_images = list(test_dir.glob("*.JPG"))[:5]
    
    print("\nRename Preview:")
    print("-" * 80)
    print(f"{'Original Filename':<20} {'Original Date':<20} {'Corrected Date':<20} {'New Filename'}")
    print("-" * 80)
    
    for img_path in test_images:
        exif_dt = get_exif_datetime(img_path)
        if not exif_dt:
            print(f"No EXIF data found for {img_path.name}")
            continue
            
        # Apply the offset
        corrected_dt = exif_dt + datetime.timedelta(days=offset_days)
        new_name = generate_new_filename(img_path, corrected_dt)
        
        print(f"{img_path.name:<20} {exif_dt.strftime('%Y-%m-%d %H:%M:%S'):<20} "
              f"{corrected_dt.strftime('%Y-%m-%d %H:%M:%S'):<20} {new_name}")


if __name__ == "__main__":
    test_rename_preview()
    
    print("\nTo perform the actual renaming, use the photo_renamer.py script with:")
    print("python photo_renamer.py 'Entocam test 2025-05-17' --days 418 --dry-run")
    print("Remove --dry-run to actually perform the renaming")
