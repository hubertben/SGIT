#!/usr/bin/env python3
import os
import stat
import subprocess
import sys

def main():
    """Install sgit to make it available system-wide."""
    # Get the absolute path of the sgit.py script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sgit_script = os.path.join(script_dir, "sgit.py")
    
    # Check if the script exists
    if not os.path.exists(sgit_script):
        # If not, create sgit.py from scratch
        with open("sgit.py", "w") as f:
            f.write('''
#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import re

VERSION_FILE = '.version'

def get_current_version():
    """Read the current version from the version file."""
    if not os.path.exists(VERSION_FILE):
        # Initialize with 0.0.0 if file doesn't exist
        set_version('00.00.00')
        return '00.00.00'
    
    with open(VERSION_FILE, 'r') as f:
        version = f.read().strip()
    
    # Validate version format
    if not re.match(r'^\d{2}\.\d{2}\.\d{2}$', version):
        print(f"Error: Invalid version format in {VERSION_FILE}. Using default 00.00.00.")
        set_version('00.00.00')
        return '00.00.00'
    
    return version

def set_version(version):
    """Write the version to the version file."""
    # Validate version format
    if not re.match(r'^\d{2}\.\d{2}\.\d{2}$', version):
        print("Error: Version must be in format xx.xx.xx.")
        sys.exit(1)
    
    with open(VERSION_FILE, 'w') as f:
        f.write(version)
    
    print(f"Version set to {version}")

def increment_version(major=False, minor=False, patch=False):
    """Increment version based on flags."""
    current = get_current_version()
    major_num, minor_num, patch_num = map(int, current.split('.'))
    
    if major:
        major_num += 1
        minor_num = 0
        patch_num = 0
    elif minor:
        minor_num += 1
        patch_num = 0
    elif patch:
        patch_num += 1
    
    # Check for overflow
    if major_num > 99:
        print("Warning: Major version exceeded 99, resetting to 99.")
        major_num = 99
    if minor_num > 99:
        print("Warning: Minor version exceeded 99, resetting to 99.")
        minor_num = 99
    if patch_num > 99:
        print("Warning: Patch version exceeded 99, resetting to 99.")
        patch_num = 99
    
    new_version = f"{major_num:02d}.{minor_num:02d}.{patch_num:02d}"
    set_version(new_version)
    
    # Create indicator string
    if major:
        return f"*{new_version}"
    elif minor:
        parts = new_version.split('.')
        return f"{parts[0]}.*{parts[1]}.{parts[2]}"
    elif patch:
        parts = new_version.split('.')
        return f"{parts[0]}.{parts[1]}.*{parts[2]}"
    else:
        return new_version

def run_command(command, capture_output=False):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(command, shell=True, text=True, 
                               capture_output=capture_output, check=True)
        if capture_output:
            return result.stdout.strip()
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr.strip() if e.stderr else 'Unknown error'}")
        sys.exit(1)

def get_status():
    """Get git status and parse changed files."""
    status_output = run_command("git status --porcelain", capture_output=True)
    if not status_output:
        print("No changes to commit.")
        sys.exit(0)
    
    files = []
    for line in status_output.split('\n'):
        if not line.strip():
            continue
        
        status_code = line[:2].strip()
        file_path = line[3:].strip()
        
        status_desc = {
            'M': 'Modified',
            'A': 'Added',
            'D': 'Deleted',
            'R': 'Renamed',
            'C': 'Copied',
            'U': 'Updated but unmerged',
            '??': 'Untracked'
        }
        
        # Get the description based on the first character of the status code
        description = status_desc.get(status_code[0], 'Changed')
        
        files.append({
            'path': file_path,
            'status': status_code,
            'description': description
        })
    
    return files

def display_files(files):
    """Display the list of files with status and index."""
    print("\\nFiles to be committed:")
    print("-" * 60)
    for i, file in enumerate(files, 1):
        print(f"{i:2}. [{file['description']:8}] {file['path']}")
    print("-" * 60)

def prompt_remove_files(files):
    """Prompt user to remove files from the commit."""
    display_files(files)
    
    remove_input = input("\\nEnter indices to remove (comma-separated) or press Enter to continue: ").strip()
    
    if not remove_input:
        return files
    
    try:
        indices_to_remove = [int(idx.strip()) for idx in remove_input.split(',')]
        filtered_files = [file for i, file in enumerate(files, 1) if i not in indices_to_remove]
        
        print(f"\\nRemoved {len(files) - len(filtered_files)} files from commit.")
        return filtered_files
    except ValueError:
        print("Invalid input. Proceeding with all files.")
        return files

def main():
    # Check for set version command
    if len(sys.argv) > 1 and sys.argv[1] == '-s' and len(sys.argv) == 3:
        set_version(sys.argv[2])
        return
    
    # Parse flags for version increments
    major, minor, patch = False, False, False
    
    for arg in sys.argv[1:]:
        if arg == '-M':
            major = True
        elif arg == '-m':
            minor = True
        elif arg == '-p':
            patch = True
    
    # Get the version with indicator
    version_indicator = increment_version(major, minor, patch)
    
    # Get the files to be committed
    files = get_status()
    
    if not files:
        print("No changes to commit.")
        return
    
    # Prompt to remove files
    files = prompt_remove_files(files)
    
    if not files:
        print("No files selected for commit.")
        return
    
    # Clear any previous staging
    run_command("git reset")
    
    # Add the selected files
    for file in files:
        run_command(f"git add '{file['path']}'")
    
    # Prompt for commit message
    commit_message = input("\\nEnter commit message (or press Enter for timestamp): ").strip()
    
    if not commit_message:
        commit_message = f"Automatic commit at {int(time.time())}"
    
    # Format the commit message with version
    formatted_message = f"[{version_indicator}] {commit_message}"
    
    # Commit and push
    print(f"\\nCommitting with message: {formatted_message}")
    run_command(f"git commit -m '{formatted_message}'")
    
    print("\\nPushing to remote...")
    run_command("git push")
    
    print("\\nCompleted successfully.")

if __name__ == "__main__":
    main()

''')
        sgit_script = os.path.join(os.getcwd(), "sgit.py")
        print(f"Created sgit.py script at {sgit_script}")
        
    # Make the script executable
    os.chmod(sgit_script, os.stat(sgit_script).st_mode | stat.S_IEXEC)
    
    # Determine installation location
    install_dir = os.path.expanduser("~/.local/bin")
    os.makedirs(install_dir, exist_ok=True)
    
    # Create symlink for sgit
    sgit_link = os.path.join(install_dir, "sgit")
    if os.path.exists(sgit_link):
        os.unlink(sgit_link)
    os.symlink(sgit_script, sgit_link)
    
    # Create symlink for sgit-s (will be handled by the main script)
    sgit_s_link = os.path.join(install_dir, "sgit-s")
    if os.path.exists(sgit_s_link):
        os.unlink(sgit_s_link)
    os.symlink(sgit_script, sgit_s_link)
    
    # Check if the install directory is in PATH
    path_env = os.environ.get('PATH', '')
    if install_dir not in path_env.split(':'):
        print(f"\nWARNING: {install_dir} is not in your PATH.")
        print("Add the following line to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
        print(f"export PATH=\"{install_dir}:$PATH\"")
        
        # Ask if user wants to add to PATH
        add_to_path = input("\nWould you like to add it to your PATH now? (y/n): ").lower().strip()
        if add_to_path == 'y':
            shell = os.environ.get('SHELL', '').split('/')[-1]
            profile_file = f"~/.{shell}rc"
            
            if shell in ['bash', 'zsh', 'sh']:
                expanded_profile = os.path.expanduser(profile_file)
                with open(expanded_profile, 'a') as f:
                    f.write(f'\n# Added by sgit installer\nexport PATH="{install_dir}:$PATH"\n')
                print(f"Added to {profile_file}. Please restart your terminal or run:")
                print(f"source {profile_file}")
            else:
                print(f"Unsupported shell: {shell}. Please add the PATH manually.")
    
    print("\nInstallation completed!")
    print(f"The 'sgit' command is now available. Run it from any git repository.")
    print("Usage:")
    print("  sgit         - Commit and push all changes with the current version")
    print("  sgit -M      - Increment major version, then commit and push")
    print("  sgit -m      - Increment minor version, then commit and push")
    print("  sgit -p      - Increment patch version, then commit and push")
    print("  sgit-s x.y.z - Set the version to x.y.z")

if __name__ == "__main__":
    main()