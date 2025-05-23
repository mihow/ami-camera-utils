#!/usr/bin/env python3
"""
Photo Renamer - Renames image files based on their EXIF timestamp.
Can correct for incorrect timestamps in the EXIF data.
"""

import os
import datetime
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import exifread
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Rename photos based on EXIF timestamp")
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
        for tag in ['EXIF DateTimeOriginal', 'EXIF DateTimeDigitized', 
                    'Image DateTime']:
            if tag in tags:
                date_str = str(tags[tag])
                # EXIF datetime format: 'YYYY:MM:DD HH:MM:SS'
                dt = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                return dt
        return None
    except Exception as e:
        console.print(f"[red]Error reading EXIF data from {file_path}: {e}[/red]")
        return None


def apply_date_offset(dt: Optional[datetime.datetime], 
                      days: int = 0, 
                      hours: int = 0, 
                      minutes: int = 0) -> Optional[datetime.datetime]:
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


def generate_new_filepath(original_path: Path, 
                          timestamp: datetime.datetime, 
                          prefix: str = "entocamtest",
                          output_dir: Optional[Path] = None) -> Path:
    """
    Generate a new file path based on the original file and the timestamp.
    
    Args:
        original_path: Original file path
        timestamp: Datetime to use in the filename
        prefix: Prefix to use for the new filename
        output_dir: Optional output directory (if None, uses original directory)
        
    Returns:
        New file path with timestamp
    """
    # Format: prefix-YYYYMMDDHHmmSS.ext
    time_str = timestamp.strftime("%Y%m%d%H%M%S")
    extension = original_path.suffix.lower()
    new_filename = f"{prefix}-{time_str}{extension}"
    
    if output_dir:
        return output_dir / new_filename
    else:
        return original_path.parent / new_filename


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


def process_images(directory: Path, 
                   days_offset: int = 0,
                   hours_offset: int = 0, 
                   minutes_offset: int = 0,
                   recursive: bool = True,
                   prefix: str = "entocamtest",
                   output_dir: Optional[Path] = None,
                   dry_run: bool = False) -> List[Dict[str, Any]]:
    """
    Process images in the directory and prepare for renaming.
    
    Args:
        directory: Directory containing images
        days_offset: Days to add to the timestamp (can be negative)
        hours_offset: Hours to add to the timestamp (can be negative)
        minutes_offset: Minutes to add to the timestamp (can be negative)
        recursive: Whether to search recursively
        prefix: Prefix for the new filenames
        output_dir: Optional output directory
        dry_run: If True, don't actually rename files
        
    Returns:
        List of dictionaries with file info
    """
    image_files = find_image_files(directory, recursive)
    console.print(f"[green]Found {len(image_files)} image files in {directory}[/green]")
    
    if output_dir and not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[blue]Output directory: {output_dir}[/blue]")
    
    results = []
    
    for image_path in image_files:
        exif_dt = get_exif_datetime(image_path)
        
        if not exif_dt:
            console.print(f"[yellow]No EXIF datetime found for {image_path}[/yellow]")
            continue
            
        corrected_dt = apply_date_offset(exif_dt, days_offset, hours_offset, 
                                         minutes_offset)
        new_path = generate_new_filepath(image_path, corrected_dt, prefix, 
                                         output_dir)
        
        results.append({
            "original_path": image_path,
            "exif_datetime": exif_dt,
            "corrected_datetime": corrected_dt,
            "new_path": new_path,
            "is_copy": output_dir is not None
        })
    
    return results


def display_summary(results: List[Dict[str, Any]]) -> None:
    """
    Display a summary of the proposed renaming operations.
    
    Args:
        results: List of dictionaries with file info
    """
    if not results:
        console.print("[yellow]No files to rename.[/yellow]")
        return
    
    operation = "Copy" if results[0]["is_copy"] else "Rename"
    table = Table(title=f"Files to {operation}")
    table.add_column("Original Filename", style="cyan")
    table.add_column("Original EXIF Date", style="magenta")
    table.add_column("Corrected Date", style="green")
    table.add_column("New Path", style="yellow")
    
    for item in results:
        table.add_row(
            str(item["original_path"].name),
            item["exif_datetime"].strftime("%Y-%m-%d %H:%M:%S"),
            item["corrected_datetime"].strftime("%Y-%m-%d %H:%M:%S"),
            str(item["new_path"])
        )
    
    console.print(table)
    console.print(f"[bold green]Total files to {operation.lower()}: {len(results)}[/bold green]")


def process_files(results: List[Dict[str, Any]]) -> int:
    """
    Process files based on the processed results (rename or copy).
    
    Args:
        results: List of dictionaries with file info
        
    Returns:
        Number of files successfully processed
    """
    processed_count = 0
    
    for item in results:
        try:
            if item["new_path"].exists():
                console.print(f"[red]Cannot process {item['original_path']} - destination already exists: {item['new_path']}[/red]")
                continue
            
            if item["is_copy"]:
                # Copy to output directory
                shutil.copy2(item["original_path"], item["new_path"])
                console.print(f"[green]Copied: {item['original_path']} -> {item['new_path']}[/green]")
            else:
                # Rename in place
                item["original_path"].rename(item["new_path"])
                console.print(f"[green]Renamed: {item['original_path'].name} -> {item['new_path'].name}[/green]")
            
            processed_count += 1
        except Exception as e:
            console.print(f"[red]Error processing {item['original_path']}: {e}[/red]")
    
    return processed_count


@app.command()
def rename(
    directory: Path = typer.Argument(
        ..., 
        exists=True, 
        file_okay=False, 
        dir_okay=True, 
        help="Directory containing images to rename"
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory for renamed files (required unless --inplace is used)"
    ),
    inplace: bool = typer.Option(
        False,
        "--inplace",
        help="Rename files in place rather than copying to output directory"
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
    prefix: str = typer.Option(
        "entocamtest", 
        "--prefix", 
        "-p", 
        help="Prefix for the new filenames"
    ),
    dry_run: bool = typer.Option(
        False, 
        "--dry-run", 
        "-n", 
        help="Show what would be done without actually renaming files"
    ),
    yes: bool = typer.Option(
        False, 
        "--yes", 
        "-y", 
        help="Skip confirmation prompt and proceed with renaming"
    )
) -> None:
    """
    Rename image files based on their EXIF timestamp.
    
    This utility processes images from the specified directory and renames them
    according to their EXIF timestamp (with optional correction), following the
    format: prefix-YYYYMMDDHHmmSS.ext
    
    Either --output-dir must be specified (files will be copied) or --inplace
    must be used (files will be renamed in their current location).
    """
    # Validate arguments
    if not inplace and not output_dir:
        console.print("[red]Error: Either --output-dir must be specified or --inplace must be used.[/red]")
        console.print("[yellow]Use --output-dir to copy files to a new directory, or --inplace to rename files in their current location.[/yellow]")
        raise typer.Exit(1)
    
    if inplace and output_dir:
        console.print("[red]Error: Cannot use both --inplace and --output-dir options together.[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold]Processing images in {directory}[/bold]")
    
    if inplace:
        console.print("[bold]Files will be renamed in place[/bold]")
        actual_output_dir = None
    else:
        console.print(f"[bold]Files will be copied to: {output_dir}[/bold]")
        actual_output_dir = output_dir
    
    if days_offset or hours_offset or minutes_offset:
        offset_info = ", ".join(
            f"{value} {name}" for name, value in 
            [("days", days_offset), ("hours", hours_offset), ("minutes", minutes_offset)] 
            if value
        )
        console.print(f"[bold]Applying time correction: {offset_info}[/bold]")
    
    results = process_images(
        directory=directory,
        days_offset=days_offset,
        hours_offset=hours_offset,
        minutes_offset=minutes_offset,
        recursive=recursive,
        prefix=prefix,
        output_dir=actual_output_dir,
        dry_run=dry_run
    )
    
    display_summary(results)
    
    if dry_run:
        console.print("[yellow]Dry run complete. No files were processed.[/yellow]")
        return
    
    if not results:
        console.print("[yellow]No files to process. Exiting.[/yellow]")
        return
    
    operation = "copy" if actual_output_dir else "rename"
    if not yes:
        confirmed = typer.confirm(f"Do you want to proceed with {operation}ing?")
        if not confirmed:
            console.print("[yellow]Operation cancelled. No files were processed.[/yellow]")
            return
    
    processed_count = process_files(results)
    console.print(f"[bold green]Successfully processed {processed_count} out of {len(results)} files.[/bold green]")


if __name__ == "__main__":
    app()
