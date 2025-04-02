# SGit - Semantic Git Tool

SGit is a custom Git workflow tool that integrates semantic versioning (SemVer 2.0) with your Git operations. It streamlines your commit process while maintaining proper versioning.

## Features

- **Semantic Versioning**: Automatically tracks your project version in SemVer 2.0 format
- **Interactive Commits**: Displays changed files and allows selective committing
- **Streamlined Workflow**: Combines git add, commit, and push into one command
- **Version Tracking**: Stores version in a `.version` file in your repository
- **Smart Commit Messages**: Automatically formats commit messages with version information

## Installation

1. Clone or download this repository
2. Run the installer script:

```bash
python install.py
```

This will:
- Make the script executable
- Create symlinks in `~/.local/bin`
- Optionally add the directory to your PATH

## Usage

### Basic Commands

```bash
# Regular commit with current version
sgit

# Increment major version (x+1.0.0)
sgit -M

# Increment minor version (x.y+1.0)
sgit -m

# Increment patch version (x.y.z+1)
sgit -p

# Set version to specific value
sgit-s xx.xx.xx
```

### Workflow

When you run `sgit`, the following will happen:

1. The script gets the current version from `.version` file
2. If a version flag is provided (-M, -m, -p), it increments accordingly
3. It displays all changed files with status (Modified, Added, Deleted, etc.)
4. You can choose to remove specific files from the commit
5. You'll be prompted for a commit message (or press Enter for timestamp)
6. The script formats the commit message with version information
7. Git add, commit, and push operations are executed

### Version Format

Versions are displayed in the format `MM.mm.pp` where:
- MM: Major version (00-99)
- mm: Minor version (00-99)
- pp: Patch version (00-99)

In commit messages, an asterisk (*) is placed next to the component that was incremented:

- `[*01.00.00] ...` - Major version incremented
- `[01.*02.00] ...` - Minor version incremented
- `[01.02.*03] ...` - Patch version incremented

## Version Rules

- Major increment resets minor and patch to 00
- Minor increment resets patch to 00
- Maximum value for any component is 99
- All components are displayed as two digits (e.g., 01.03.07)

## Requirements

- Python 3.6+
- Git

## License

MIT