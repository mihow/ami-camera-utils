#!/usr/bin/env python3
"""
Test that the photo renamer skips existing files in the destination.
"""

import datetime
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ami_camera_utils.photo_renamer import process_images


def test_skip_existing_files():
    """Test that existing files in destination are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Create test image file
        test_image = tmp_path / "test.jpg"
        test_image.touch()
        
        # Create existing file in output directory with expected name
        existing_file = output_dir / "entocamtest-20240324103045.jpg"
        existing_file.touch()
        
        # Mock EXIF datetime extraction
        with patch("ami_camera_utils.photo_renamer.get_exif_datetime") as mock_exif:
            mock_exif.return_value = datetime.datetime(2024, 3, 24, 10, 30, 45)
            
            results = process_images(
                directory=tmp_path,
                output_dir=output_dir,
                recursive=False
            )
            
            # Should return empty results since the file already exists
            assert len(results) == 0


def test_process_only_new_files():
    """Test that only new files (non-existing) are processed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Create test image files
        test_image1 = tmp_path / "test1.jpg"
        test_image1.touch()
        test_image2 = tmp_path / "test2.jpg"
        test_image2.touch()
        
        # Create existing file for only one of them
        existing_file = output_dir / "entocamtest-20240324103045.jpg"
        existing_file.touch()
        
        # Mock EXIF datetime extraction to return different times
        def mock_exif_side_effect(file_path):
            if "test1" in str(file_path):
                return datetime.datetime(2024, 3, 24, 10, 30, 45)  # Will exist
            else:
                return datetime.datetime(2024, 3, 24, 11, 30, 45)  # Won't exist
        
        with patch("ami_camera_utils.photo_renamer.get_exif_datetime") as mock_exif:
            mock_exif.side_effect = mock_exif_side_effect
            
            results = process_images(
                directory=tmp_path,
                output_dir=output_dir,
                recursive=False
            )
            
            # Should only process test2.jpg since test1.jpg already exists
            assert len(results) == 1
            assert "test2.jpg" in str(results[0]["original_path"])
            assert "entocamtest-20240324113045.jpg" in str(results[0]["new_path"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
