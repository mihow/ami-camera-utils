#!/usr/bin/env python3
"""
Test script to demonstrate photo sampling at time intervals
"""

from pathlib import Path


def test_sampling_preview():
    """Show how to use photo_sampler.py with example commands"""
    test_dir = Path("Entocam test 2025-05-17")
    
    print("\nPhoto Sampler Usage Examples:")
    print("=" * 80)
    
    print("\n1. Basic Usage - Sample at 10-minute intervals (default):")
    print(f"   python photo_sampler.py \"{test_dir}\" --dry-run")
    
    print("\n2. Custom Interval - Sample at 30-minute intervals:")
    print(f"   python photo_sampler.py \"{test_dir}\" "
          f"--interval 30 --dry-run")
    
    print("\n3. Custom Output Directory:")
    print(f"   python photo_sampler.py \"{test_dir}\" "
          f"--output-dir \"30min-samples\" "
          f"--interval 30 --dry-run")
    
    print("\n4. With Time Correction (for cameras with incorrect dates):")
    print(f"   python photo_sampler.py \"{test_dir}\" --days 418 --dry-run")
    
    print("\n5. Preserving Directory Structure:")
    print(f"   python photo_sampler.py \"{test_dir}\" "
          f"--preserve-structure --dry-run")
    
    print("\n6. Execute Without Confirmation:")
    print(f"   python photo_sampler.py \"{test_dir}\" --yes")
    
    print("\n7. Non-recursive (only process images in the top level):")
    print(f"   python photo_sampler.py \"{test_dir}\" "
          f"--no-recursive --dry-run")
    
    print("\nRemove the --dry-run flag to actually copy the sampled files.")


if __name__ == "__main__":
    test_sampling_preview()
    
    print("\nFull Command Reference:")
    print("python photo_sampler.py --help")
