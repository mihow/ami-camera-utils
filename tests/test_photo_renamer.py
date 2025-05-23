#!/usr/bin/env python3
"""
Pytest tests for photo_renamer module.
"""

import datetime
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from ami_camera_utils.photo_renamer import (
    get_exif_datetime,
    apply_date_offset,
    generate_new_filepath,
    find_image_files,
)


class TestExifDatetime:
    """Test EXIF datetime extraction."""
    
    @patch("ami_camera_utils.photo_renamer.exifread.process_file")
    @patch("builtins.open", new_callable=mock_open, 
           read_data=b"fake image data")
    def test_get_exif_datetime_success(self, mock_file, mock_process):
        """Test successful EXIF datetime extraction."""
        # Mock EXIF tags
        mock_tags = {
            'EXIF DateTimeOriginal': '2024:03:24 10:30:45'
        }
        mock_process.return_value = mock_tags
        
        result = get_exif_datetime(Path("test.jpg"))
        
        expected = datetime.datetime(2024, 3, 24, 10, 30, 45)
        assert result == expected
        mock_file.assert_called_once()
        mock_process.assert_called_once()
    
    @patch("ami_camera_utils.photo_renamer.exifread.process_file")
    @patch("builtins.open", new_callable=mock_open, 
           read_data=b"fake image data")
    def test_get_exif_datetime_no_tags(self, mock_file, mock_process):
        """Test when no EXIF datetime tags are found."""
        mock_process.return_value = {}
        
        result = get_exif_datetime(Path("test.jpg"))
        
        assert result is None
    
    @patch("ami_camera_utils.photo_renamer.exifread.process_file")
    @patch("builtins.open", side_effect=IOError("File not found"))
    def test_get_exif_datetime_file_error(self, mock_file, mock_process):
        """Test when file cannot be read."""
        result = get_exif_datetime(Path("nonexistent.jpg"))
        
        assert result is None


class TestDateOffset:
    """Test date offset functionality."""
    
    def test_apply_date_offset_positive(self):
        """Test applying positive offset."""
        dt = datetime.datetime(2024, 3, 24, 10, 30, 45)
        result = apply_date_offset(dt, days=418, hours=2, minutes=30)
        
        expected = dt + datetime.timedelta(days=418, hours=2, minutes=30)
        assert result == expected
    
    def test_apply_date_offset_negative(self):
        """Test applying negative offset."""
        dt = datetime.datetime(2025, 5, 16, 10, 30, 45)
        result = apply_date_offset(dt, days=-418, hours=-2, minutes=-30)
        
        expected = dt + datetime.timedelta(days=-418, hours=-2, minutes=-30)
        assert result == expected
    
    def test_apply_date_offset_none_input(self):
        """Test applying offset to None datetime."""
        result = apply_date_offset(None, days=1)
        assert result is None


class TestFilepathGeneration:
    """Test new filepath generation."""
    
    def test_generate_new_filepath_basic(self):
        """Test basic new filepath generation."""
        original = Path("/test/dir/original.jpg")
        timestamp = datetime.datetime(2025, 5, 16, 14, 30, 45)
        
        result = generate_new_filepath(original, timestamp)
        
        expected = Path("/test/dir/entocamtest-20250516143045.jpg")
        assert result == expected
    
    def test_generate_new_filepath_custom_prefix(self):
        """Test new filepath generation with custom prefix."""
        original = Path("/test/dir/original.JPG")
        timestamp = datetime.datetime(2025, 5, 16, 14, 30, 45)
        
        result = generate_new_filepath(original, timestamp, prefix="custom")
        
        expected = Path("/test/dir/custom-20250516143045.jpg")
        assert result == expected
    
    def test_generate_new_filepath_with_output_dir(self):
        """Test new filepath generation with output directory."""
        original = Path("/test/dir/original.png")
        timestamp = datetime.datetime(2025, 5, 16, 14, 30, 45)
        output_dir = Path("/output")
        
        result = generate_new_filepath(
            original, timestamp, output_dir=output_dir
        )
        
        expected = Path("/output/entocamtest-20250516143045.png")
        assert result == expected


class TestImageFileFinding:
    """Test image file discovery."""
    
    def test_find_image_files_basic(self):
        """Test finding image files in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create test files
            (tmp_path / "image1.jpg").touch()
            (tmp_path / "image2.PNG").touch()
            (tmp_path / "document.txt").touch()
            (tmp_path / "photo.tiff").touch()
            
            result = find_image_files(tmp_path, recursive=False)
            
            # Should find 3 image files
            assert len(result) == 3
            image_names = {f.name for f in result}
            assert "image1.jpg" in image_names
            assert "image2.PNG" in image_names
            assert "photo.tiff" in image_names
            assert "document.txt" not in image_names
    
    def test_find_image_files_recursive(self):
        """Test finding image files recursively."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create nested structure
            subdir = tmp_path / "subdir"
            subdir.mkdir()
            
            (tmp_path / "top.jpg").touch()
            (subdir / "nested.png").touch()
            
            result = find_image_files(tmp_path, recursive=True)
            
            assert len(result) == 2
            names = {f.name for f in result}
            assert "top.jpg" in names
            assert "nested.png" in names
    
    def test_find_image_files_non_recursive(self):
        """Test finding image files non-recursively."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create nested structure
            subdir = tmp_path / "subdir"
            subdir.mkdir()
            
            (tmp_path / "top.jpg").touch()
            (subdir / "nested.png").touch()
            
            result = find_image_files(tmp_path, recursive=False)
            
            assert len(result) == 1
            assert result[0].name == "top.jpg"


def test_import_module():
    """Test that the module can be imported properly."""
    from ami_camera_utils import photo_renamer
    assert hasattr(photo_renamer, 'app')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
