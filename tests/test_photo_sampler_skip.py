#!/usr/bin/env python3
"""
Test that the photo sampler skips existing files in the destination.
"""

import datetime
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from ami_camera_utils.photo_sampler import process_images_for_sampling


def test_skip_existing_files_in_sampling():
    """Test that existing files in destination are skipped during sampling."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Create test image files
        test_image1 = tmp_path / "test1.jpg"
        test_image1.touch()
        test_image2 = tmp_path / "test2.jpg"
        test_image2.touch()
        
        # Create existing file in output directory
        existing_file = output_dir / "test1.jpg"
        existing_file.touch()
        
        # Mock EXIF datetime extraction to return different times
        def mock_exif_side_effect(file_path):
            if "test1" in str(file_path):
                return datetime.datetime(2024, 3, 24, 10, 30, 45)
            else:
                return datetime.datetime(2024, 3, 24, 10, 45, 45)  # 15 min later
        
        with patch("ami_camera_utils.photo_sampler.get_exif_datetime") as mock_exif:
            mock_exif.side_effect = mock_exif_side_effect
            
            samples, skipped_count = process_images_for_sampling(
                directory=tmp_path,
                interval_minutes=10,
                recursive=False,
                output_dir=output_dir
            )
            
            # Should skip test1.jpg since it exists, and include test2.jpg
            assert len(samples) == 1
            assert skipped_count == 1
            assert "test2.jpg" in str(samples[0]["original_path"])


def test_no_skipping_when_no_output_dir():
    """Test that no skipping occurs when no output directory is specified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        
        # Create test image files
        test_image1 = tmp_path / "test1.jpg"
        test_image1.touch()
        test_image2 = tmp_path / "test2.jpg"
        test_image2.touch()
        
        # Mock EXIF datetime extraction
        def mock_exif_side_effect(file_path):
            if "test1" in str(file_path):
                return datetime.datetime(2024, 3, 24, 10, 30, 45)
            else:
                return datetime.datetime(2024, 3, 24, 10, 45, 45)
        
        with patch("ami_camera_utils.photo_sampler.get_exif_datetime") as mock_exif:
            mock_exif.side_effect = mock_exif_side_effect
            
            samples, skipped_count = process_images_for_sampling(
                directory=tmp_path,
                interval_minutes=10,
                recursive=False,
                output_dir=None  # No output directory
            )
            
            # Should not skip any files when no output directory is specified
            assert len(samples) == 2
            assert skipped_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
