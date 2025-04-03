#!/usr/bin/env python3
"""
sgit - Semantic Versioning Git Pusher

A custom Git wrapper that manages semantic versioning (2.0) with your Git repositories.
Automatically tracks version numbers and provides a streamlined Git workflow.

Usage:
    sgit          - Regular commit with no version increment
    sgit -M       - Increment major version (resets minor and patch to 00)
    sgit -m       - Increment minor version (resets patch to 00)
    sgit -p       - Increment patch version
    sgit -s X.Y.Z - Set version to specific value (e.g., sgit -s 01.02.03)

Features:
    - Semantic versioning integration with Git commits
    - File selection/deselection before committing
    - Automatic version tracking
    - Default timestamped commit messages
"""

import os
import sys
import subprocess
import time
import re
import argparse
from datetime import datetime

VERSION_FILE = "sgit.version"
DEFAULT_VERSION = "00.00.01"  # Start with 00.00.01 if no version file exists

def run_command(command, capture_output=True):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               text=True, capture_output=capture_output)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"\033[91mError executing: {command}\033[0m")
        print(f"\033[91m{e.stderr}\033[0m")
        sys.exit(1)

def get_git_root():
    """Get the root directory of the Git repository."""
    try:
        return run_command("git rev-parse --show-toplevel")
    except:
        print("\033[91mError: Not in a Git repository.\033[0m")
        sys.exit(1)

def get_current_version():
    """Get the current version from the sgit.version file."""
    git_root = get_git_root()
    version_path = os.path.join(git_root, VERSION_FILE)
    
    if os.path.exists(version_path):
        with open(version_path, 'r') as f:
            version = f.read().strip()
            # Validate the version format
            if re.match(r'^\d{2}\.\d{2}\.\d{2}$', version):
                return version
            else:
                print(f"\033[93mWarning: Invalid version format in {VERSION_FILE}, resetting to {DEFAULT_VERSION}\033[0m")
    else:
        print(f"\033[93mCreating new {VERSION_FILE} with initial version {DEFAULT_VERSION}\033[0m")
    
    # If file doesn't exist or has invalid format, create with default version
    with open(version_path, 'w') as f:
        f.write(DEFAULT_VERSION)
    
    return DEFAULT_VERSION

def set_version(version):
    """Set the version in the sgit.version file."""
    # Validate version format
    if not re.match(r'^\d{2}\.\d{2}\.\d{2}$', version):
        print("\033[91mError: Version must be in format XX.XX.XX (e.g., 01.02.03)\033[0m")
        sys.exit(1)
    
    git_root = get_git_root()
    version_path = os.path.join(git_root, VERSION_FILE)
    
    with open(version_path, 'w') as f:
        f.write(version)
    
    print(f"\033[92mVersion set to {version}\033[0m")
    return version

def increment_version(current_version, major=False, minor=False, patch=False):
    """Increment the version based on which component should be increased."""
    parts = current_version.split('.')
    major_val = int(parts[0])
    minor_val = int(parts[1])
    patch_val = int(parts[2])
    
    # Store which components were incremented for adding stars later
    incremented = []
    
    if major:
        major_val = (major_val + 1) % 100
        minor_val = 0
        patch_val = 0
        incremented.append('major')
    
    if minor:
        minor_val = (minor_val + 1) % 100
        patch_val = 0
        incremented.append('minor')
    
    if patch:
        patch_val = (patch_val + 1) % 100
        incremented.append('patch')
    
    # Format with leading zeros
    new_version = f"{major_val:02d}.{minor_val:02d}.{patch_val:02d}"
    
    return new_version, incremented

def format_version_with_stars(version, incremented):
    """Format the version with stars next to incremented components."""
    if not incremented:
        return version  # No stars if nothing was incremented
    
    parts = version.split('.')
    
    # Create the version string with stars
    version_with_stars = ""
    if 'major' in incremented:
        version_with_stars += f"*{parts[0]}."
    else:
        version_with_stars += f"{parts[0]}."
        
    if 'minor' in incremented:
        version_with_stars += f"*{parts[1]}."
    else:
        version_with_stars += f"{parts[1]}."
        
    if 'patch' in incremented:
        version_with_stars += f"*{parts[2]}"
    else:
        version_with_stars += f"{parts[2]}"
    
    return version_with_stars

def get_changed_files():
    """Get a list of files changed in the working directory."""
    # Get all changes (including untracked files)
    status_output = run_command("git status --porcelain")
    
    if not status_output:
        print("\033[93mNo changes to commit.\033[0m")
        sys.exit(0)
    
    files = []
    for line in status_output.split('\n'):
        if line.strip():
            # The first two characters are the status codes, but we must not strip them
            # as that would remove leading spaces that are part of the format
            status_code = line[:2].strip()
            filename = line[2:].strip()

            if status_code == '??':
                status_text = "\033[92mINSERT\033[0m"
            
            elif status_code == 'D':
                status_text = "\033[91mDELETE\033[0m"
            
            elif status_code == 'M':
                status_text = "\033[93mUPDATE\033[0m"
                
            else:
                status_text = "Unknown"

            files.append((filename, status_text, status_code))
    
    return files

def main():
    parser = argparse.ArgumentParser(description="Semantic Versioning Git Helper")
    parser.add_argument('-M', action='store_true', help='Increment major version')
    parser.add_argument('-m', action='store_true', help='Increment minor version')
    parser.add_argument('-p', action='store_true', help='Increment patch version')
    parser.add_argument('-s', metavar='VERSION', help='Set specific version (XX.XX.XX)')
    
    args = parser.parse_args()
    
    # Handle setting specific version with sgit -s
    if args.s:
        set_version(args.s)
        return
    
    # Get current version
    current_version = get_current_version()
    
    # Handle version increments
    incremented = []
    if args.M or args.m or args.p:
        new_version, incremented = increment_version(current_version, args.M, args.m, args.p)
        set_version(new_version)
        current_version = new_version
    
    # Get changed files
    changed_files = get_changed_files()
    
    # Show files to be committed
    print("\n\033[1mFiles to be committed:\033[0m")
    for i, (filename, status_text, _) in enumerate(changed_files, 1):
        print(f"{i}. {status_text} {filename}")
    
    # Ask if user wants to remove any files
    print("\nEnter indices of files to exclude (comma-separated) or press Enter to include all:")
    exclude_input = input("> ").strip()
    
    # Create a list for files to add
    files_to_add = []
    
    if exclude_input:
        # Parse the indices to exclude
        try:
            exclude_indices = [int(idx.strip()) for idx in exclude_input.split(',') if idx.strip().isdigit()]
            # Only include files not in the exclude list
            files_to_add = [file[0] for i, file in enumerate(changed_files, 1) if i not in exclude_indices]
        except ValueError:
            print("\033[93mInvalid input. Including all files.\033[0m")
            files_to_add = [file[0] for file in changed_files]
        
        if not files_to_add:
            print("\033[93mNo files selected for commit. Exiting.\033[0m")
            sys.exit(0)
    else:
        # Include all files if no exclusion
        files_to_add = [file[0] for file in changed_files]
    
    # Display the list of files that will be added
    print("\n\033[1mFiles that will be added to commit:\033[0m")
    for i, filename in enumerate(files_to_add, 1):
        print(f"{i}. {filename}")
    
    # Add files to staging
    if files_to_add:
        # First reset any staged files
        run_command("git reset", capture_output=False)
        
        # Use different approaches to handle file adding
        try:
            # Method 1: Use git add . and then remove files we don't want
            run_command("git add .", capture_output=False)
            
            # If we're not adding all files, we need to remove some
            all_files = [file[0] for file in changed_files]
            files_to_remove = [file for file in all_files if file not in files_to_add]
            
            # Remove any files that should be excluded
            for file in files_to_remove:
                print(f"\033[94mExcluding: {file}\033[0m")
                run_command(f"git reset HEAD \"{file}\"", capture_output=False)
                
            print(f"\n\033[92mAdded {len(files_to_add)} file(s) to commit\033[0m")
        except Exception as e:
            print(f"\033[91mError adding files: {str(e)}\033[0m")
            sys.exit(1)
    
    # Get commit message
    print("\nEnter commit message (press Enter for timestamp):")
    commit_message = input("> ").strip()
    
    if not commit_message:
        # Use Unix timestamp as default message
        commit_message = f"Automatic commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Format version with stars for the commit
    version_display = format_version_with_stars(current_version, incremented)
    
    # Create full commit message with version
    full_commit_message = f"[{version_display}] {commit_message}"
    
    # Commit and push
    print(f"\n\033[94mCommitting with message: \"{full_commit_message}\"\033[0m")
    run_command(f"git commit -m \"{full_commit_message}\"", capture_output=False)
    
    print("\n\033[94mPushing to remote repository...\033[0m")
    push_result = run_command("git push", capture_output=True)
    
    print(f"\n\033[92mSuccessfully pushed with version {current_version}\033[0m")

if __name__ == "__main__":
    main()