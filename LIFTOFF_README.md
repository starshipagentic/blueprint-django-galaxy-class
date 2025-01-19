# 🚀 LIFTOFF - AI-Powered Documentation Generator

LIFTOFF is a powerful documentation generator that helps you define and refine your project's mission using AI assistance.

## Features

- 🤖 AI-powered documentation generation
- 📝 Interactive mission definition
- 🔄 Iterative refinement process
- 🖥️ VS Code integration
- 🔍 Dry-run mode for previewing changes
- 🐛 Debug mode for troubleshooting

## Prerequisites

- Python 3.9+
- VS Code (for macOS integration)
- Anthropic API key (for Claude 3.5 access)

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Basic launch:
```bash
python LIFTOFF.py launch
```

Available options:
```bash
python LIFTOFF.py launch --debug      # Enable debug output
python LIFTOFF.py launch --dry-run    # Preview changes without modifying files

# Git operations
python LIFTOFF.py push               # Push changes (will prompt for commit message)
python LIFTOFF.py push -m "message"  # Push changes with specific commit message
python LIFTOFF.py push --debug       # Push with detailed progress output
```

## How It Works

1. **Mission Definition**: Opens and helps complete MISSION.md
2. **AI Assistance**: Uses Claude 3.5 to generate detailed content
3. **Interactive Refinement**: Allows iterative improvements
4. **Version Control**: Automatically commits changes (when not in dry-run mode)

## Configuration

The tool uses several environment variables and configuration options:
- VS Code integration (macOS only)
- AI model selection (currently using Claude 3.5 Sonnet)
- Git integration for version control

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms specified in the LICENSE file.

## Support

For issues and feature requests, please open an issue in the repository.
