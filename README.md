# sgit - Semantic Versioning Git Pusher

## Setup Instructions

1. Save the script as `sgit` in a directory that's in your PATH (e.g., `/usr/local/bin/` or `~/bin/`)
2. Make the script executable:
   ```bash
   chmod +x /path/to/sgit
   ```
3. You can create a symbolic link for the `sgit-s` command:
   ```bash
   ln -s /path/to/sgit /path/to/sgit-s
   ```
   Or you can simply use the `-s` parameter with the `sgit` command.

## Usage

### Initialize or set a specific version
```bash
sgit -s 01.00.00
```

### Increment version and push changes
```bash
# Increment patch version (default if no flags provided)
sgit

# Increment minor version
sgit -m

# Increment major version
sgit -M

# You can combine flags (though not typically needed)
sgit -M -m -p
```

### Process

When you run `sgit`:

1. It reads the current version from `sgit.version` (creates the file if it doesn't exist)
2. Increments the version according to the provided flags
3. Lists all files with changes, showing if they were modified/added/deleted
4. Prompts you to exclude any files from the commit (enter numbers as comma-separated list)
5. Prompts for a commit message (press Enter to use Unix timestamp)
6. Formats the commit message as `[MM.*mm.pp] commit message` (with * indicating what was incremented)
7. Performs `git add`, `git commit`, and `git push` operations

## Features

- Automatically creates and maintains a version file in your repository
- Follows Semantic Versioning 2.0 principles
- Displays versioning with stars to indicate which component was incremented
- Allows selective file staging
- Falls back to timestamp commit messages when none provided
- Always formats version components as two digits (e.g., 01.03.07)
- Resets minor and patch versions to 00 when incrementing major version
- Resets patch version to 00 when incrementing minor version