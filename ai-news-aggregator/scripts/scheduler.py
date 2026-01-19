#!/usr/bin/env python3
"""
Scheduler setup script for AI News Aggregator.
Generates platform-specific scheduled task configurations.
"""

import os
import sys
import platform
from pathlib import Path
from textwrap import dedent


def get_script_path() -> Path:
    """Get absolute path to scraper.py."""
    return Path(__file__).parent / 'scraper.py'


def get_python_path() -> str:
    """Get Python interpreter path."""
    return sys.executable


def generate_launchd_plist(script_path: Path, python_path: str) -> str:
    """Generate macOS launchd plist configuration."""
    # Run daily at 9:00 AM
    plist_content = dedent(f'''
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.user.ai-news-aggregator</string>

        <key>ProgramArguments</key>
        <array>
            <string>{python_path}</string>
            <string>{script_path}</string>
        </array>

        <key>StartCalendarInterval</key>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>

        <key>StandardOutPath</key>
        <string>/tmp/ai-news-aggregator.log</string>

        <key>StandardErrorPath</key>
        <string>/tmp/ai-news-aggregator-error.log</string>
    </dict>
    </plist>
    ''').strip()

    return plist_content


def generate_cron_config(script_path: Path, python_path: str) -> str:
    """Generate Linux/Unix cron configuration."""
    # Run daily at 9:00 AM
    cron_line = f'0 9 * * * {python_path} {script_path}'

    return cron_line


def setup_macos():
    """Setup launchd on macOS."""
    script_path = get_script_path()
    python_path = get_python_path()

    plist_content = generate_launchd_plist(script_path, python_path)

    # Save plist file
    plist_dir = Path.home() / 'Library' / 'LaunchAgents'
    plist_dir.mkdir(parents=True, exist_ok=True)
    plist_file = plist_dir / 'com.user.ai-news-aggregator.plist'

    with open(plist_file, 'w') as f:
        f.write(plist_content)

    print(f"✅ LaunchAgent created: {plist_file}")
    print("\nNext steps:")
    print("1. Load the agent:")
    print(f"   launchctl load {plist_file}")
    print("\n2. Verify it's loaded:")
    print("   launchctl list | grep ai-news")
    print("\n3. Test run immediately:")
    print("   launchctl start com.user.ai-news-aggregator")
    print("\n4. View logs:")
    print("   tail -f /tmp/ai-news-aggregator.log")


def setup_linux():
    """Setup cron on Linux."""
    script_path = get_script_path()
    python_path = get_python_path()

    cron_config = generate_cron_config(script_path, python_path)

    print("=== Cron Configuration ===\n")
    print(f"# Add this line to crontab (run: crontab -e)")
    print(cron_config)
    print("\n\nNext steps:")
    print("1. Edit your crontab: crontab -e")
    print("2. Add the line above")
    print("3. Save and exit")
    print("\n4. Verify cron job:")
    print("   crontab -l")


def main():
    """Main entry point."""
    print("=== AI News Aggregator Scheduler Setup ===\n")

    system = platform.system()

    if system == "Darwin":
        print("Detected: macOS")
        setup_macos()
    elif system == "Linux":
        print("Detected: Linux")
        setup_linux()
    else:
        print(f"Unsupported platform: {system}")
        print("\nManual setup required. The scraper script is located at:")
        print(f"  {get_script_path()}")
        print(f"\nRun it with: {get_python_path()} {get_script_path()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
