import os
import pytest
import name_service
import save_service
from pathlib import Path

def test_format_timestamp_success():
    """
    Test that a valid millisecond timestamp converts correctly to YYYYMMDD_HHMMSS.
    """
    # 1716382105000 milliseconds equals 2024-05-22 15:48:25 (depending on timezone)
    # Let's test if the function processes the math without crashing and returns a string
    sample_timestamp = "1716382105000"
    result = name_service.format_timestamp(sample_timestamp)
    
    assert result is not None
    assert len(result) == 15  # Length of 'YYYYMMDD_HHMMSS'
    assert "_" in result

def test_format_timestamp_invalid():
    """
    Test that the timestamp function handles invalid input gracefully by returning None.
    """
    invalid_timestamp = "this_is_not_a_number"
    result = name_service.format_timestamp(invalid_timestamp)
    assert result is None

def test_check_filename_no_duplicate(tmp_path):
    """
    Test that if no duplicate file exists, the filename remains unchanged.
    Uses pytest's built-in tmp_path to create a temporary test folder.
    """
    temp_dir = tmp_path / "temp"
    archive_dir = tmp_path / "archive"
    temp_dir.mkdir()
    archive_dir.mkdir()

    filename = "20260717_120000"
    final_name = save_service.check_filename(filename, str(temp_dir), str(archive_dir))
    
    assert final_name == "20260717_120000.mp4"

def test_check_filename_with_duplicate(tmp_path):
    """
    Test that if a file already exists, the function appends (1) to the name.
    """
    temp_dir = tmp_path / "temp"
    archive_dir = tmp_path / "archive"
    temp_dir.mkdir()
    archive_dir.mkdir()

    # Create a fake file to cause a duplicate clash
    existing_file = temp_dir / "20260717_120000.mp4"
    existing_file.touch()

    filename = "20260717_120000"
    final_name = save_service.check_filename(filename, str(temp_dir), str(archive_dir))
    
    # The service should notice the existing file and append (1)
    assert final_name == "20260717_120000(1).mp4"
