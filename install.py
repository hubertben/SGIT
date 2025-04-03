#!/usr/bin/env python3
"""
install.py - SGit Installer

This script installs the sgit tool globally on your Linux system.
It handles installation paths, permissions, and creating necessary symlinks.

The script will:
1. Check for Python and Git dependencies
2. Find the best installation location
3. Install the sgit script
4. Create necessary symlinks
5. Provide usage information
"""

import os
import sys
import subprocess
import shutil
import stat
import platform
import re

# ANSI color codes for output formatting
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

# The sgit script content (copied from the sgit script)
SGIT_SCRIPT = '''#!/usr/bin/env python3
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
        print(f"\\033[91mError executing: {command}\\033[0m")
        print(f"\\033[91m{e.stderr}\\033[0m")
        sys.exit(1)

def get_git_root():
    """Get the root directory of the Git repository."""
    try:
        return run_command("git rev-parse --show-toplevel")
    except:
        print("\\033[91mError: Not in a Git repository.\\033[0m")
        sys.exit(1)

def get_current_version():
    """Get the current version from the sgit.version file."""
    git_root = get_git_root()
    version_path = os.path.join(git_root, VERSION_FILE)
    
    if os.path.exists(version_path):
        with open(version_path, 'r') as f:
            version = f.read().strip()
            # Validate the version format
            if re.match(r'^\\d{2}\\.\\d{2}\\.\\d{2}

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
    print("\\n\\033[1mFiles to be committed:\\033[0m")
    for i, (filename, status_text, _) in enumerate(changed_files, 1):
        print(f"{i}. {status_text} {filename}")
    
    # Ask if user wants to remove any files
    print("\\nEnter indices of files to exclude (comma-separated) or press Enter to include all:")
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
            print("\\033[93mInvalid input. Including all files.\\033[0m")
            files_to_add = [file[0] for file in changed_files]
        
        if not files_to_add:
            print("\\033[93mNo files selected for commit. Exiting.\\033[0m")
            sys.exit(0)
    else:
        # Include all files if no exclusion
        files_to_add = [file[0] for file in changed_files]
    
    # Display the list of files that will be added
    print("\\n\\033[1mFiles that will be added to commit:\\033[0m")
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
                print(f"\\033[94mExcluding: {file}\\033[0m")
                run_command(f"git reset HEAD \\"{file}\\"", capture_output=False)
                
            print(f"\\n\\033[92mAdded {len(files_to_add)} file(s) to commit\\033[0m")
        except Exception as e:
            print(f"\\033[91mError adding files: {str(e)}\\033[0m")
            sys.exit(1)
    
    # Get commit message
    print("\\nEnter commit message (press Enter for timestamp):")
    commit_message = input("> ").strip()
    
    if not commit_message:
        # Use Unix timestamp as default message
        commit_message = f"Automatic commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Format version with stars for the commit
    version_display = format_version_with_stars(current_version, incremented)
    
    # Create full commit message with version
    full_commit_message = f"[{version_display}] {commit_message}"
    
    # Commit and push
    print(f"\\n\\033[94mCommitting with message: \\"{full_commit_message}\\"\\033[0m")
    run_command(f"git commit -m \\"{full_commit_message}\\"", capture_output=False)
    
    print("\\n\\033[94mPushing to remote repository...\\033[0m")
    push_result = run_command("git push", capture_output=True)
    
    print(f"\\n\\033[92mSuccessfully pushed with version {current_version}\\033[0m")

if __name__ == "__main__":
    main()
"""

def print_colored(text, color=RESET, bold=False):
    """Print colored text."""
    if bold:
        print(f"{BOLD}{color}{text}{RESET}")
    else:
        print(f"{color}{text}{RESET}")

def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def check_dependencies():
    """Check if required dependencies are installed."""
    print_colored("Checking dependencies...", BLUE, bold=True)
    
    # Check Python version
    python_version = platform.python_version()
    if python_version:
        major, minor, _ = map(int, python_version.split('.'))
        if major < 3 or (major == 3 and minor < 6):
            print_colored(f"Error: Python 3.6+ required, found {python_version}", RED)
            sys.exit(1)
        print_colored(f"✓ Python {python_version} detected", GREEN)
    else:
        print_colored("Error: Python 3.6+ is required", RED)
        sys.exit(1)
    
    # Check Git installation
    git_version = run_command("git --version")
    if git_version:
        print_colored(f"✓ {git_version} detected", GREEN)
    else:
        print_colored("Error: Git is required but not found", RED)
        sys.exit(1)
    
    print()

def get_install_location():
    """Determine the best location to install the script."""
    print_colored("Finding the best installation location...", BLUE, bold=True)
    
    # Option 1: /usr/local/bin (preferred, requires root)
    if os.access("/usr/local/bin", os.W_OK):
        print_colored("✓ /usr/local/bin is writable", GREEN)
        return "/usr/local/bin"
    
    # Option 2: ~/bin if it exists and is in PATH
    home_bin = os.path.expanduser("~/bin")
    if os.path.exists(home_bin):
        if home_bin in os.environ.get("PATH", ""):
            print_colored(f"✓ {home_bin} exists and is in PATH", GREEN)
            return home_bin
        else:
            print_colored(f"✓ {home_bin} exists but is not in PATH", YELLOW)
            print_colored("  Will add to PATH in shell configuration", BLUE)
            return home_bin
    
    # Option 3: Create ~/bin
    print_colored(f"Creating {home_bin} directory", BLUE)
    os.makedirs(home_bin, exist_ok=True)
    print_colored(f"✓ {home_bin} created", GREEN)
    return home_bin

def update_shell_config(bin_path):
    """Update shell configuration to include the bin path in PATH."""
    # Determine which shell is being used
    shell = os.path.basename(os.environ.get("SHELL", ""))
    home = os.path.expanduser("~")
    
    config_file = None
    config_line = f'export PATH="$PATH:{bin_path}"'
    
    if shell == "bash":
        config_file = os.path.join(home, ".bashrc")
    elif shell == "zsh":
        config_file = os.path.join(home, ".zshrc")
    elif shell == "fish":
        config_file = os.path.join(home, ".config/fish/config.fish")
        config_line = f'set -gx PATH $PATH {bin_path}'
    
    if config_file:
        # Check if PATH already contains bin_path
        with open(config_file, 'a+') as f:
            f.seek(0)
            if bin_path not in f.read():
                f.write(f"\n# Added by sgit installer\n{config_line}\n")
                print_colored(f"✓ Added {bin_path} to PATH in {config_file}", GREEN)
                print_colored(f"  Please run 'source {config_file}' or restart your terminal", YELLOW)
            else:
                print_colored(f"✓ {bin_path} already in PATH", GREEN)
    else:
        print_colored(f"Could not detect shell configuration file. Please add {bin_path} to your PATH manually.", YELLOW)

def install_sgit(install_path):
    """Install the sgit script to the specified location."""
    print_colored("\nInstalling sgit...", BLUE, bold=True)
    
    # Paths for the script and symlink
    sgit_path = os.path.join(install_path, "sgit")
    sgit_s_path = os.path.join(install_path, "sgit-s")
    
    # Write the script
    with open(sgit_path, 'w') as f:
        f.write(SGIT_SCRIPT)
    
    # Make executable
    os.chmod(sgit_path, os.stat(sgit_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    print_colored(f"✓ Installed script to {sgit_path}", GREEN)
    
    # Create symlink for sgit-s
    if os.path.exists(sgit_s_path):
        os.remove(sgit_s_path)
    
    # Create symlink (or copy if symlinks not supported)
    try:
        os.symlink(sgit_path, sgit_s_path)
        print_colored(f"✓ Created symlink at {sgit_s_path}", GREEN)
    except:
        # Fallback to copy if symlink fails
        shutil.copy2(sgit_path, sgit_s_path)
        print_colored(f"✓ Created copy at {sgit_s_path} (symlink failed)", YELLOW)
    
    return sgit_path

def show_usage_info(sgit_path):
    """Show usage information for the installed sgit tool."""
    print_colored("\nSGit Installation Complete!", GREEN, bold=True)
    print_colored("\nUsage Examples:", BLUE, bold=True)
    print_colored("  sgit                  - Commit changes with current version", RESET)
    print_colored("  sgit -M               - Increment major version and commit", RESET)
    print_colored("  sgit -m               - Increment minor version and commit", RESET)
    print_colored("  sgit -p               - Increment patch version and commit", RESET)
    print_colored("  sgit -s 01.02.03      - Set version to 01.02.03", RESET)
    
    # Check if sgit is in PATH
    if sgit_path not in os.environ.get("PATH", "").split(os.pathsep):
        print_colored("\nNOTE: You may need to restart your terminal or source your shell configuration", YELLOW)
        print_colored("      file before using sgit if it was installed to a new directory.", YELLOW)

def main():
    """Main installation function."""
    print_colored("\n=== SGit - Semantic Versioning Git Tool Installer ===\n", BLUE, bold=True)
    
    # Check dependencies
    check_dependencies()
    
    # Get installation location
    install_path = get_install_location()
    
    # Update PATH if needed
    if install_path == os.path.expanduser("~/bin") and install_path not in os.environ.get("PATH", ""):
        update_shell_config(install_path)
    
    # Install the script
    sgit_path = install_sgit(install_path)
    
    # Show usage information
    show_usage_info(sgit_path)
    
    print_colored("\nThank you for installing SGit!\n", GREEN, bold=True)

if __name__ == "__main__":
    main()
, version):
                return version
            else:
                print(f"\\033[93mWarning: Invalid version format in {VERSION_FILE}, resetting to {DEFAULT_VERSION}\\033[0m")
    else:
        print(f"\\033[93mCreating new {VERSION_FILE} with initial version {DEFAULT_VERSION}\\033[0m")
    
    # If file doesn't exist or has invalid format, create with default version
    with open(version_path, 'w') as f:
        f.write(DEFAULT_VERSION)
    
    return DEFAULT_VERSION

def set_version(version):
    """Set the version in the sgit.version file."""
    # Validate version format
    if not re.match(r'^\\d{2}\\.\\d{2}\\.\\d{2}

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
    print("\\n\\033[1mFiles to be committed:\\033[0m")
    for i, (filename, status_text, _) in enumerate(changed_files, 1):
        print(f"{i}. {status_text} {filename}")
    
    # Ask if user wants to remove any files
    print("\\nEnter indices of files to exclude (comma-separated) or press Enter to include all:")
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
            print("\\033[93mInvalid input. Including all files.\\033[0m")
            files_to_add = [file[0] for file in changed_files]
        
        if not files_to_add:
            print("\\033[93mNo files selected for commit. Exiting.\\033[0m")
            sys.exit(0)
    else:
        # Include all files if no exclusion
        files_to_add = [file[0] for file in changed_files]
    
    # Display the list of files that will be added
    print("\\n\\033[1mFiles that will be added to commit:\\033[0m")
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
                print(f"\\033[94mExcluding: {file}\\033[0m")
                run_command(f"git reset HEAD \\"{file}\\"", capture_output=False)
                
            print(f"\\n\\033[92mAdded {len(files_to_add)} file(s) to commit\\033[0m")
        except Exception as e:
            print(f"\\033[91mError adding files: {str(e)}\\033[0m")
            sys.exit(1)
    
    # Get commit message
    print("\\nEnter commit message (press Enter for timestamp):")
    commit_message = input("> ").strip()
    
    if not commit_message:
        # Use Unix timestamp as default message
        commit_message = f"Automatic commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Format version with stars for the commit
    version_display = format_version_with_stars(current_version, incremented)
    
    # Create full commit message with version
    full_commit_message = f"[{version_display}] {commit_message}"
    
    # Commit and push
    print(f"\\n\\033[94mCommitting with message: \\"{full_commit_message}\\"\\033[0m")
    run_command(f"git commit -m \\"{full_commit_message}\\"", capture_output=False)
    
    print("\\n\\033[94mPushing to remote repository...\\033[0m")
    push_result = run_command("git push", capture_output=True)
    
    print(f"\\n\\033[92mSuccessfully pushed with version {current_version}\\033[0m")

if __name__ == "__main__":
    main()
"""

def print_colored(text, color=RESET, bold=False):
    """Print colored text."""
    if bold:
        print(f"{BOLD}{color}{text}{RESET}")
    else:
        print(f"{color}{text}{RESET}")

def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def check_dependencies():
    """Check if required dependencies are installed."""
    print_colored("Checking dependencies...", BLUE, bold=True)
    
    # Check Python version
    python_version = platform.python_version()
    if python_version:
        major, minor, _ = map(int, python_version.split('.'))
        if major < 3 or (major == 3 and minor < 6):
            print_colored(f"Error: Python 3.6+ required, found {python_version}", RED)
            sys.exit(1)
        print_colored(f"✓ Python {python_version} detected", GREEN)
    else:
        print_colored("Error: Python 3.6+ is required", RED)
        sys.exit(1)
    
    # Check Git installation
    git_version = run_command("git --version")
    if git_version:
        print_colored(f"✓ {git_version} detected", GREEN)
    else:
        print_colored("Error: Git is required but not found", RED)
        sys.exit(1)
    
    print()

def get_install_location():
    """Determine the best location to install the script."""
    print_colored("Finding the best installation location...", BLUE, bold=True)
    
    # Option 1: /usr/local/bin (preferred, requires root)
    if os.access("/usr/local/bin", os.W_OK):
        print_colored("✓ /usr/local/bin is writable", GREEN)
        return "/usr/local/bin"
    
    # Option 2: ~/bin if it exists and is in PATH
    home_bin = os.path.expanduser("~/bin")
    if os.path.exists(home_bin):
        if home_bin in os.environ.get("PATH", ""):
            print_colored(f"✓ {home_bin} exists and is in PATH", GREEN)
            return home_bin
        else:
            print_colored(f"✓ {home_bin} exists but is not in PATH", YELLOW)
            print_colored("  Will add to PATH in shell configuration", BLUE)
            return home_bin
    
    # Option 3: Create ~/bin
    print_colored(f"Creating {home_bin} directory", BLUE)
    os.makedirs(home_bin, exist_ok=True)
    print_colored(f"✓ {home_bin} created", GREEN)
    return home_bin

def update_shell_config(bin_path):
    """Update shell configuration to include the bin path in PATH."""
    # Determine which shell is being used
    shell = os.path.basename(os.environ.get("SHELL", ""))
    home = os.path.expanduser("~")
    
    config_file = None
    config_line = f'export PATH="$PATH:{bin_path}"'
    
    if shell == "bash":
        config_file = os.path.join(home, ".bashrc")
    elif shell == "zsh":
        config_file = os.path.join(home, ".zshrc")
    elif shell == "fish":
        config_file = os.path.join(home, ".config/fish/config.fish")
        config_line = f'set -gx PATH $PATH {bin_path}'
    
    if config_file:
        # Check if PATH already contains bin_path
        with open(config_file, 'a+') as f:
            f.seek(0)
            if bin_path not in f.read():
                f.write(f"\n# Added by sgit installer\n{config_line}\n")
                print_colored(f"✓ Added {bin_path} to PATH in {config_file}", GREEN)
                print_colored(f"  Please run 'source {config_file}' or restart your terminal", YELLOW)
            else:
                print_colored(f"✓ {bin_path} already in PATH", GREEN)
    else:
        print_colored(f"Could not detect shell configuration file. Please add {bin_path} to your PATH manually.", YELLOW)

def install_sgit(install_path):
    """Install the sgit script to the specified location."""
    print_colored("\nInstalling sgit...", BLUE, bold=True)
    
    # Paths for the script and symlink
    sgit_path = os.path.join(install_path, "sgit")
    sgit_s_path = os.path.join(install_path, "sgit-s")
    
    # Write the script
    with open(sgit_path, 'w') as f:
        f.write(SGIT_SCRIPT)
    
    # Make executable
    os.chmod(sgit_path, os.stat(sgit_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    print_colored(f"✓ Installed script to {sgit_path}", GREEN)
    
    # Create symlink for sgit-s
    if os.path.exists(sgit_s_path):
        os.remove(sgit_s_path)
    
    # Create symlink (or copy if symlinks not supported)
    try:
        os.symlink(sgit_path, sgit_s_path)
        print_colored(f"✓ Created symlink at {sgit_s_path}", GREEN)
    except:
        # Fallback to copy if symlink fails
        shutil.copy2(sgit_path, sgit_s_path)
        print_colored(f"✓ Created copy at {sgit_s_path} (symlink failed)", YELLOW)
    
    return sgit_path

def show_usage_info(sgit_path):
    """Show usage information for the installed sgit tool."""
    print_colored("\nSGit Installation Complete!", GREEN, bold=True)
    print_colored("\nUsage Examples:", BLUE, bold=True)
    print_colored("  sgit                  - Commit changes with current version", RESET)
    print_colored("  sgit -M               - Increment major version and commit", RESET)
    print_colored("  sgit -m               - Increment minor version and commit", RESET)
    print_colored("  sgit -p               - Increment patch version and commit", RESET)
    print_colored("  sgit -s 01.02.03      - Set version to 01.02.03", RESET)
    
    # Check if sgit is in PATH
    if sgit_path not in os.environ.get("PATH", "").split(os.pathsep):
        print_colored("\nNOTE: You may need to restart your terminal or source your shell configuration", YELLOW)
        print_colored("      file before using sgit if it was installed to a new directory.", YELLOW)

def main():
    """Main installation function."""
    print_colored("\n=== SGit - Semantic Versioning Git Tool Installer ===\n", BLUE, bold=True)
    
    # Check dependencies
    check_dependencies()
    
    # Get installation location
    install_path = get_install_location()
    
    # Update PATH if needed
    if install_path == os.path.expanduser("~/bin") and install_path not in os.environ.get("PATH", ""):
        update_shell_config(install_path)
    
    # Install the script
    sgit_path = install_sgit(install_path)
    
    # Show usage information
    show_usage_info(sgit_path)
    
    print_colored("\nThank you for installing SGit!\n", GREEN, bold=True)

if __name__ == "__main__":
    main()
, version):
        print("\\033[91mError: Version must be in format XX.XX.XX (e.g., 01.02.03)\\033[0m")
        sys.exit(1)
    
    git_root = get_git_root()
    version_path = os.path.join(git_root, VERSION_FILE)
    
    with open(version_path, 'w') as f:
        f.write(version)
    
    print(f"\\033[92mVersion set to {version}\\033[0m")
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
        print("\\033[93mNo changes to commit.\\033[0m")
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
    print("\\n\\033[1mFiles to be committed:\\033[0m")
    for i, (filename, status_text, _) in enumerate(changed_files, 1):
        print(f"{i}. {status_text} {filename}")
    
    # Ask if user wants to remove any files
    print("\\nEnter indices of files to exclude (comma-separated) or press Enter to include all:")
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
            print("\\033[93mInvalid input. Including all files.\\033[0m")
            files_to_add = [file[0] for file in changed_files]
        
        if not files_to_add:
            print("\\033[93mNo files selected for commit. Exiting.\\033[0m")
            sys.exit(0)
    else:
        # Include all files if no exclusion
        files_to_add = [file[0] for file in changed_files]
    
    # Display the list of files that will be added
    print("\\n\\033[1mFiles that will be added to commit:\\033[0m")
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
                print(f"\\033[94mExcluding: {file}\\033[0m")
                run_command(f"git reset HEAD \\"{file}\\"", capture_output=False)
                
            print(f"\\n\\033[92mAdded {len(files_to_add)} file(s) to commit\\033[0m")
        except Exception as e:
            print(f"\\033[91mError adding files: {str(e)}\\033[0m")
            sys.exit(1)
    
    # Get commit message
    print("\\nEnter commit message (press Enter for timestamp):")
    commit_message = input("> ").strip()
    
    if not commit_message:
        # Use Unix timestamp as default message
        commit_message = f"Automatic commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Format version with stars for the commit
    version_display = format_version_with_stars(current_version, incremented)
    
    # Create full commit message with version
    full_commit_message = f"[{version_display}] {commit_message}"
    
    # Commit and push
    print(f"\\n\\033[94mCommitting with message: \\"{full_commit_message}\\"\\033[0m")
    run_command(f"git commit -m \\"{full_commit_message}\\"", capture_output=False)
    
    print("\\n\\033[94mPushing to remote repository...\\033[0m")
    push_result = run_command("git push", capture_output=True)
    
    print(f"\\n\\033[92mSuccessfully pushed with version {current_version}\\033[0m")

if __name__ == "__main__":
    main()
'''

def print_colored(text, color=RESET, bold=False):
    """Print colored text."""
    if bold:
        print(f"{BOLD}{color}{text}{RESET}")
    else:
        print(f"{color}{text}{RESET}")

def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def check_dependencies():
    """Check if required dependencies are installed."""
    print_colored("Checking dependencies...", BLUE, bold=True)
    
    # Check Python version
    python_version = platform.python_version()
    if python_version:
        major, minor, _ = map(int, python_version.split('.'))
        if major < 3 or (major == 3 and minor < 6):
            print_colored(f"Error: Python 3.6+ required, found {python_version}", RED)
            sys.exit(1)
        print_colored(f"✓ Python {python_version} detected", GREEN)
    else:
        print_colored("Error: Python 3.6+ is required", RED)
        sys.exit(1)
    
    # Check Git installation
    git_version = run_command("git --version")
    if git_version:
        print_colored(f"✓ {git_version} detected", GREEN)
    else:
        print_colored("Error: Git is required but not found", RED)
        sys.exit(1)
    
    print()

def get_install_location():
    """Determine the best location to install the script."""
    print_colored("Finding the best installation location...", BLUE, bold=True)
    
    # Option 1: /usr/local/bin (preferred, requires root)
    if os.access("/usr/local/bin", os.W_OK):
        print_colored("✓ /usr/local/bin is writable", GREEN)
        return "/usr/local/bin"
    
    # Option 2: ~/bin if it exists and is in PATH
    home_bin = os.path.expanduser("~/bin")
    if os.path.exists(home_bin):
        if home_bin in os.environ.get("PATH", ""):
            print_colored(f"✓ {home_bin} exists and is in PATH", GREEN)
            return home_bin
        else:
            print_colored(f"✓ {home_bin} exists but is not in PATH", YELLOW)
            print_colored("  Will add to PATH in shell configuration", BLUE)
            return home_bin
    
    # Option 3: Create ~/bin
    print_colored(f"Creating {home_bin} directory", BLUE)
    os.makedirs(home_bin, exist_ok=True)
    print_colored(f"✓ {home_bin} created", GREEN)
    return home_bin

def update_shell_config(bin_path):
    """Update shell configuration to include the bin path in PATH."""
    # Determine which shell is being used
    shell = os.path.basename(os.environ.get("SHELL", ""))
    home = os.path.expanduser("~")
    
    config_file = None
    config_line = f'export PATH="$PATH:{bin_path}"'
    
    if shell == "bash":
        config_file = os.path.join(home, ".bashrc")
    elif shell == "zsh":
        config_file = os.path.join(home, ".zshrc")
    elif shell == "fish":
        config_file = os.path.join(home, ".config/fish/config.fish")
        config_line = f'set -gx PATH $PATH {bin_path}'
    
    if config_file:
        # Check if PATH already contains bin_path
        with open(config_file, 'a+') as f:
            f.seek(0)
            if bin_path not in f.read():
                f.write(f"\n# Added by sgit installer\n{config_line}\n")
                print_colored(f"✓ Added {bin_path} to PATH in {config_file}", GREEN)
                print_colored(f"  Please run 'source {config_file}' or restart your terminal", YELLOW)
            else:
                print_colored(f"✓ {bin_path} already in PATH", GREEN)
    else:
        print_colored(f"Could not detect shell configuration file. Please add {bin_path} to your PATH manually.", YELLOW)

def install_sgit(install_path):
    """Install the sgit script to the specified location."""
    print_colored("\nInstalling sgit...", BLUE, bold=True)
    
    # Paths for the script and symlink
    sgit_path = os.path.join(install_path, "sgit")
    sgit_s_path = os.path.join(install_path, "sgit-s")
    
    # Write the script
    with open(sgit_path, 'w') as f:
        f.write(SGIT_SCRIPT)
    
    # Make executable
    os.chmod(sgit_path, os.stat(sgit_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    
    print_colored(f"✓ Installed script to {sgit_path}", GREEN)
    
    # Create symlink for sgit-s
    if os.path.exists(sgit_s_path):
        os.remove(sgit_s_path)
    
    # Create symlink (or copy if symlinks not supported)
    try:
        os.symlink(sgit_path, sgit_s_path)
        print_colored(f"✓ Created symlink at {sgit_s_path}", GREEN)
    except:
        # Fallback to copy if symlink fails
        shutil.copy2(sgit_path, sgit_s_path)
        print_colored(f"✓ Created copy at {sgit_s_path} (symlink failed)", YELLOW)
    
    return sgit_path

def show_usage_info(sgit_path):
    """Show usage information for the installed sgit tool."""
    print_colored("\nSGit Installation Complete!", GREEN, bold=True)
    print_colored("\nUsage Examples:", BLUE, bold=True)
    print_colored("  sgit                  - Commit changes with current version", RESET)
    print_colored("  sgit -M               - Increment major version and commit", RESET)
    print_colored("  sgit -m               - Increment minor version and commit", RESET)
    print_colored("  sgit -p               - Increment patch version and commit", RESET)
    print_colored("  sgit -s 01.02.03      - Set version to 01.02.03", RESET)
    
    # Check if sgit is in PATH
    if sgit_path not in os.environ.get("PATH", "").split(os.pathsep):
        print_colored("\nNOTE: You may need to restart your terminal or source your shell configuration", YELLOW)
        print_colored("      file before using sgit if it was installed to a new directory.", YELLOW)

def main():
    """Main installation function."""
    print_colored("\n=== SGit - Semantic Versioning Git Tool Installer ===\n", BLUE, bold=True)
    
    # Check dependencies
    check_dependencies()
    
    # Get installation location
    install_path = get_install_location()
    
    # Update PATH if needed
    if install_path == os.path.expanduser("~/bin") and install_path not in os.environ.get("PATH", ""):
        update_shell_config(install_path)
    
    # Install the script
    sgit_path = install_sgit(install_path)
    
    # Show usage information
    show_usage_info(sgit_path)
    
    print_colored("\nThank you for installing SGit!\n", GREEN, bold=True)

if __name__ == "__main__":
    main()