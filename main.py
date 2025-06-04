#!/usr/bin/env python3
"""
Project Runner Script
=====================

This script allows you to easily run any of the three main scripts in your project:
1. Card Market Scraper (generates Excel files from scraped prices)
2. Card Price Analyzer (analyzes individual card prices)
3. Deck Price Analyzer (analyzes total deck costs)

HOW TO RUN:
-----------
1. Open terminal/command prompt
2. Navigate to your project directory
3. Run: python run_project.py
4. Choose which script to run by entering 1, 2, or 3
5. Press Enter to execute

REQUIREMENTS:
-------------
- Make sure all your script files exist in the same directory
- Ensure all dependencies for each script are installed
- Run from the project root directory
"""

import os
import sys
import subprocess


def display_menu():
    """Display the main menu options"""
    print("\n" + "=" * 50)
    print("         PROJECT SCRIPT RUNNER")
    print("=" * 50)
    print("Choose which script to run:")
    print()
    print("1. Card Market Scraper")
    print("   └── Scrapes prices from CardMarket (SLOWEST)")
    print("   └── Generates Excel files")
    print("   └── File: main_script.py")
    print()
    print("2. Card Price Analyzer")
    print("   └── Analyzes individual card prices")
    print("   └── Uses Excel from option 1")
    print("   └── File: card_price_analyzer.py")
    print()
    print("3. Deck Price Analyzer")
    print("   └── Analyzes total deck costs")
    print("   └── Uses data from Excel files")
    print("   └── File: deck_price_analyzer.py")
    print()
    print("0. Exit")
    print("=" * 50)


def check_file_exists(filepath):
    """Check if a file exists and return True/False"""
    if os.path.exists(filepath):
        return True
    else:
        print(f"ERROR: File not found - {filepath}")
        return False


def run_script(script_path):
    """Run a Python script and handle errors"""
    try:
        print(f"\nRunning: {script_path}")
        print("-" * 30)

        # Run the script
        result = subprocess.run([sys.executable, script_path],
                                capture_output=False,
                                text=True)

        if result.returncode == 0:
            print(f"\n✅ Script completed successfully!")
        else:
            print(f"\n❌ Script finished with errors (exit code: {result.returncode})")

    except Exception as e:
        print(f"\n❌ Error running script: {e}")


def main():
    """Main function to run the script selector"""

    # Define script paths (now all in root directory)
    scripts = {
        '1': {
            'name': 'Card Market Scraper',
            'path': 'main_script.py',
            'description': 'This will scrape CardMarket prices (takes the longest time)'
        },
        '2': {
            'name': 'Card Price Analyzer',
            'path': 'card_price_analyzer.py',
            'description': 'This will analyze individual card prices from Excel'
        },
        '3': {
            'name': 'Deck Price Analyzer',
            'path': 'deck_price_analyzer.py',
            'description': 'This will analyze total deck costs'
        }
    }

    while True:
        display_menu()

        choice = input("Enter your choice (0-3): ").strip()

        if choice == '0':
            print("\nGoodbye! 👋")
            break

        elif choice in scripts:
            script_info = scripts[choice]

            # Check if file exists
            if not check_file_exists(script_info['path']):
                input("\nPress Enter to continue...")
                continue

            # Confirm before running
            print(f"\nYou selected: {script_info['name']}")
            print(f"Description: {script_info['description']}")

            confirm = input("\nDo you want to run this script? (y/n): ").strip().lower()

            if confirm in ['y', 'yes']:
                run_script(script_info['path'])
            else:
                print("Operation cancelled.")

            input("\nPress Enter to return to menu...")

        else:
            print("\n❌ Invalid choice! Please enter 0, 1, 2, or 3.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
