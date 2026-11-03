# AI Mod Analyzer — Version 0.1.0

A Windows desktop foundation for a future AI-assisted Skyrim mod analyzer.

## What works in this first build

- Dark desktop interface with Dashboard, Scanner, Troubleshooter, and Settings pages.
- Initial Skyrim Special Edition installation detection using common registry and Steam paths.
- Initial Vortex and Mod Organizer 2 detection using common install locations.
- Reads the current Windows user’s Skyrim Special Edition `plugins.txt`.
- Checks for `loadorder.txt` and counts files in the game's `Data` directory.
- Captures a local symptom report in the Troubleshooter screen.
- Saves the preferred AI mode locally (Hybrid, Local, Cloud, or Disabled).

## Important limitations

This is a foundation build, not a complete mod analyzer yet.

- Detection is best-effort. Custom Steam libraries, portable manager installations, custom profiles, and non-standard paths may need manual path configuration in a later update.
- `plugins.txt` is the standard Windows profile list and may not represent the active MO2 profile. MO2 profile-aware inventory is planned.
- Vortex mod inventory and deployment/file winners are not yet parsed.
- No plugin-record conflict analysis, LOOT sorting, crash-log interpretation, or AI diagnosis is implemented yet.
- AI mode is a saved preference only. No local model or cloud provider is connected in this version.
- The app does not modify the game, mod manager, plugins, load order, or user files.

## Requirements

- Windows 10 or Windows 11
- Python 3.11 or newer
- Internet connection for the first-time PySide6 installation

## Run

1. Extract the ZIP to a folder such as `C:\\Tools\\AI-Mod-Analyzer`.
2. Install Python 3.11+ from https://www.python.org/downloads/ if needed. During installation, enable the option to add Python to PATH.
3. Double-click `run_windows.bat`.
4. The launcher creates a local virtual environment, installs PySide6, and starts the app.

The first launch downloads PySide6. Later launches reuse the installed environment.

## Project structure

```text
AI-Mod-Analyzer/
├── main.py
├── scanner.py
├── settings.py
├── requirements.txt
├── run_windows.bat
└── README.md
```

## Next development milestone

The next milestone should add explicit game and manager path selection, accurate active-profile discovery for Vortex and MO2, manager-specific mod inventory, and a structured diagnostic report export. Keep all scanning read-only until the findings have been validated.
