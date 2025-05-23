#!/usr/bin/env python3
"""
Photo Sampler - Samples image files at specified time intervals based on their EXIF timestamp.
Copies the sampled images to a target directory without modifying the originals.
"""

import os
import shutil
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any
import exifread
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

app = typer.Typer(help="Sample photos at specific time intervals based on EXIF timestamp")
console = Console()

def get_exif_datetime(file_path: Path) -> Optional[datetime.datetime]:
    """
    Extract the datetime from the EXIF data of an image file.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        datetime object or None if no datetime information is found
    """
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            
        # Try different EXIF datetime tags in order of preference
        for tag in ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 'Image DateTime']:
            if tag in tags:
                date_str = str(tags[tag])
                # EXIF datetime format: 'YYYY:MM:DD HH:MM:SS'
                dt = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                return dt
        return None
    except Exception as e:
        console.print(f"[red]Error reading EXIF data from {file_path}: {e}[/red]")
        return None

def apply_date_offset(dt: datetime.datetime, 
                      days: int = 0, 
                      hours: int = 0, 
                      minutes: int = 0) -> datetime.datetime:
    """
    Apply an offset to a datetime object.
    
    Args:
        dt: Original datetime
        days: Number of days to add (can be negative)
        hours: Number of hours to add (can be negative)
        minutes: Number of minutes to add (can be negative)
        
    Returns:
        New datetime with the offset applied
    """
    if not dt:
        return None
    
    delta = datetime.timedelta(days=days, hours=hours, minutes=minutes)
    return dt + delta

def find_image_files(directory: Path, recursive: bool = True) -> List[Path]:
    """
    Find all image files in a directory.
    
    Args:
        directory: Directory to search
        recursive: Whether to search recursively
        
    Returns:
        List of paths to image files
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.gif', '.bmp'}
    
    if not recursive:
        return [f for f in directory.iterdir() 
                if f.is_file() and f.suffix.lower() in image_extensions]
    
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in image_extensions:
                image_files.append(file_path)
    
    return image_files

def process_images_for_sampling(
    directory: Path,
    interval_minutes: int = 10,
    days_offset: int = 0,
    hours_offset: int = 0,
    minutes_offset: int = 0,
    recursive: bool = True
) -> List[Dict[str, Any]]:
    """
    Process images in the directory and select samples based on time interval.
    
    Args:
        directory: Directory containing images
        interval_minutes: Time interval in minutes for sampling
        days_offset: Days to add to the timestamp (can be negative)
        hours_offset: Hours to add to the timestamp (can be negative)
        minutes_offset: Minutes to add to the timestamp (can be negative)
        recursive: Whether to search recursively
        
    Returns:
        List of dictionaries with file info for sampled images
    """
    image_files = find_image_files(directory, recursive)
    console.print(f"[green]Found {len(image_files)} image files in {directory}[/green]")
    
    # Create a list of (file_path, timestamp) tuples
    timestamped_files = []
    for image_path in image_files:
        exif_dt = get_exif_datetime(image_path)
        
        if not exif_dt:
            console.print(f"[yellow]No EXIF datetime found for {image_path}[/yellow]")
            continue
            
        corrected_dt = apply_date_offset(exif_dt, days_offset, hours_offset, minutes_offset)
        timestamped_files.append((image_path, corrected_dt))
    
    if not timestamped_files:
        console.print("[yellow]No images with valid timestamps found.[/yellow]")
        return []
    
    # Sort files by timestamp
    timestamped_files.sort(key=lambda x: x[1])
    
    # Group images by interval
    interval_delta = datetime.timedelta(minutes=interval_minutes)
    sampled_images = []
    
    if not timestamped_files:
        return []
    
    # Initialize with the first timestamp
    current_interval_start = timestamped_files[0][1]
    next_interval_start = current_interval_start + interval_delta
    
    # Find the first image in each interval
    for image_path, timestamp in timestamped_files:
        # If this image is in a new interval, add it to our samples
        if timestamp >= next_interval_start:
            # Update the interval markers
            while timestamp >= next_interval_start:
                current_interval_start = next_interval_start
                next_interval_start = current_interval_start + interval_delta
            
            sampled_images.append({
                "original_path": image_path,
                "timestamp": timestamp,
                "interval_start": current_interval_start
            })
        # For the very first interval, we want to include its first image
        elif len(sampled_images) == 0:
            sampled_images.append({
                "original_path": image_path,
                "timestamp": timestamp,
                "interval_start": current_interval_start
            })
    
    return sampled_images

def display_samples_summary(samples: List[Dict[str, Any]]) -> None:
    """
    Display a summary of the samples selected.
    
    Args:
        samples: List of dictionaries with file info for sampled images
    """
    if not samples:
        console.print("[yellow]No samples selected.[/yellow]")
        return
    
    table = Table(title="Selected Sample Images")
    table.add_column("Original Filename", style="cyan")
    table.add_column("Timestamp", style="magenta")
    table.add_column("Interval Start", style="green")
    
    for item in samples:
        table.add_row(
            str(item["original_path"].name),
            item["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            item["interval_start"].strftime("%Y-%m-%d %H:%M:%S"),
        )
    
    console.print(table)
    console.print(f"[bold green]Total samples selected: {len(samples)}[/bold green]")

def copy_sampled_files(samples: List[Dict[str, Any]], output_dir: Path, preserve_structure: bool = False) -> int:
    """
    Copy sampled files to the output directory.
    
    Args:
        samples: List of dictionaries with file info for sampled images
        output_dir: Directory to copy files to
        preserve_structure: Whether to preserve the directory structure
        
    Returns:
        Number of files successfully copied
    """
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
        console.print(f"[green]Created output directory: {output_dir}[/green]")
    
    copied_count = 0
    
    for item in samples:
        original_path = item["original_path"]
        
        if preserve_structure:
            # Calculate relative path from original directory
            try:
                rel_path = original_path.relative_to(original_path.parent.parent)
                target_dir = output_dir / rel_path.parent
                if not target_dir.exists():
                    target_dir.mkdir(parents=True)
            except ValueError:
                # Fallback if relative_to fails
                target_dir = output_dir
        else:
            target_dir = output_dir
        
        target_path = target_dir / original_path.name
        
        try:
            if target_path.exists():
                console.print(f"[yellow]File already exists, skipping: {target_path}[/yellow]")
                continue
                
            shutil.copy2(original_path, target_path)
            copied_count += 1
            console.print(f"[green]Copied: {original_path.name} -> {target_path}[/green]")
        except Exception as e:
            console.print(f"[red]Error copying {original_path}: {e}[/red]")
    
    return copied_count

@app.command()
def sample(
    directory: Path = typer.Argument(
        ..., 
        exists=True, 
        file_okay=False, 
        dir_okay=True, 
        help="Directory containing images to sample"
    ),
    output_dir: Path = typer.Option(
        "snapshots",
        "--output-dir", 
        "-o", 
        help="Directory to save sampled images"
    ),
    interval: int = typer.Option(
        10, 
        "--interval", 
        "-i", 
        help="Sampling interval in minutes"
    ),
    days_offset: int = typer.Option(
        0, 
        "--days", 
        "-d", 
        help="Days to add to the timestamp (can be negative)"
    ),
    hours_offset: int = typer.Option(
        0, 
        "--hours", 
        "-h", 
        help="Hours to add to the timestamp (can be negative)"
    ),
    minutes_offset: int = typer.Option(
        0, 
        "--minutes", 
        "-m", 
        help="Minutes to add to the timestamp (can be negative)"
    ),
    recursive: bool = typer.Option(
        True, 
        "--recursive/--no-recursive", 
        "-r/-nr", 
        help="Whether to search recursively"
    ),
    preserve_structure: bool = typer.Option(
        False, 
        "--preserve-structure", 
        "-p", 
        help="Preserve directory structure in output"
    ),
    dry_run: bool = typer.Option(
        False, 
        "--dry-run", 
        "-n", 
        help="Show what would be done without actually copying files"
    ),
    yes: bool = typer.Option(
        False, 
        "--yes", 
        "-y", 
        help="Skip confirmation prompt and proceed with copying"
    )
) -> None:
    """
    Sample image files at specific time intervals based on their EXIF timestamp.
    
    This utility processes images from the specified directory and selects one image
    per time interval based on the EXIF timestamp. The selected images are copied to
    the output directory.
    """
    console.print(f"[bold]Processing images in {directory}[/bold]")
    console.print(f"[bold]Sampling interval: {interval} minutes[/bold]")
    
    if days_offset or hours_offset or minutes_offset:
        offset_info = ", ".join(
            f"{value} {name}" for name, value in 
            [("days", days_offset), ("hours", hours_offset), ("minutes", minutes_offset)] 
            if value
        )
        console.print(f"[bold]Applying time correction: {offset_info}[/bold]")
    
    samples = process_images_for_sampling(
        directory=directory,
        interval_minutes=interval,
        days_offset=days_offset,
        hours_offset=hours_offset,
        minutes_offset=minutes_offset,
        recursive=recursive
    )
    
    display_samples_summary(samples)
    
    if dry_run:
        console.print(f"[yellow]Dry run complete. No files were copied. Would copy {len(samples)} files to {output_dir}[/yellow]")
        return
    
    if not samples:
        console.print("[yellow]No samples to copy. Exiting.[/yellow]")
        return
    
    if not yes:
        confirmed = typer.confirm(f"Do you want to proceed with copying {len(samples)} files to {output_dir}?")
        if not confirmed:
            console.print("[yellow]Operation cancelled. No files were copied.[/yellow]")
            return
    
    copied_count = copy_sampled_files(samples, output_dir, preserve_structure)
    console.print(f"[bold green]Successfully copied {copied_count} out of {len(samples)} files to {output_dir}.[/bold green]")

if __name__ == "__main__":
    app()
