"""
Main entry point for the CardMarket scraper application.
Provides a simple command-line interface for users.
"""

import sys
import time

import yaml
import os
from card_scraper import CardScraper


# def get_user_input():
#     """
#     Get configuration file from user input.
#
#     Returns:
#         Path to configuration file
#     """
#     print("=== CARDMARKET SCRAPER ===")
#     print("Sequential scraping for reliable results")
#     print()
#
#     config_file = input("Enter YAML config file name (or press Enter for '2009_twilight.yaml'): ").strip()
#     if not config_file:
#         config_file = 'card_lists/2009_twilight.yaml'
#
#     return config_file


def show_instructions():
    """Show basic usage instructions to the user."""
    print("\n📝 USAGE INSTRUCTIONS:")
    print("1. Make sure Chrome is running with remote debugging:")
    print("   chrome.exe --remote-debugging-port=9222 --user-data-dir=\"C:/chrome-dev\"")
    print("2. Create a YAML config file with your card list")
    print("3. Run this script and enter the config file name")
    print("4. Results will be saved to an Excel file with timestamp")
    print()


def scrape_yaml(yaml_file):
    """Main function to run the scraper."""
    try:
        # Show instructions
        show_instructions()

        # Confirm before starting
        print(f"📁 Using config file: {yaml_file}")
        time.sleep(5)

        # Initialize and run scraper
        scraper = CardScraper()
        success = scraper.scrape_cards_from_config(yaml_file)

        if success:
            print("\n✅ Scraping completed successfully!")
            print("Check the generated Excel file for results.")
        else:
            print("\n❌ Scraping failed. Please check the errors above.")
            return 1

    except KeyboardInterrupt:
        print("\n\n⏹️ Scraping cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


def manual_scrape():
    """
    Manual scraping function for testing individual URLs.
    Can be called directly for debugging purposes.
    """
    print("=== MANUAL SCRAPE MODE ===")
    url = input("Enter CardMarket URL to scrape: ").strip()
    card_name = input("Enter card name for identification: ").strip() or "Manual"

    scraper = CardScraper()
    listings = scraper.scrape_single_url(url, card_name)

    print(f"\nFound {len(listings)} listings:")
    for i, listing in enumerate(listings[:5], 1):  # Show first 5 results
        print(f"{i}. {listing['seller_username']} - {listing['price']} - {listing['condition']}")

    if len(listings) > 5:
        print(f"... and {len(listings) - 5} more listings")


def load_yaml_list(list_file_path):
    """
    Load the list of YAML files to process from _list.yaml

    Args:
        list_file_path: Path to the _list.yaml file

    Returns:
        List of YAML filenames to process
    """
    try:
        with open(list_file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            return data.get('list', [])
    except FileNotFoundError:
        print(f"❌ Error: {list_file_path} not found")
        return []
    except yaml.YAMLError as e:
        print(f"❌ Error parsing YAML file {list_file_path}: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error loading {list_file_path}: {e}")
        return []


def process_yaml_list():
    """
    Process all YAML files listed in _list.yaml

    Returns:
        Overall exit code (0 if all successful, 1 if any failed)
    """
    list_file = 'card_lists/_list.yaml'
    yaml_files = load_yaml_list(list_file)

    if not yaml_files:
        print(f"⚠️ No YAML files found in {list_file} or file could not be loaded")
        return 1

    print(f"📋 Found {len(yaml_files)} YAML files to process:")
    for yaml_file in yaml_files:
        print(f"   - {yaml_file}")
    print()

    failed_files = []
    successful_files = []

    for yaml_file in yaml_files:
        yaml_path = os.path.join('card_lists', yaml_file)

        print(f"🔄 Processing: {yaml_file}")
        print("-" * 50)

        try:
            exit_code = scrape_yaml(yaml_path)

            if exit_code == 0:
                successful_files.append(yaml_file)
                print(f"✅ Successfully processed: {yaml_file}")
            else:
                failed_files.append(yaml_file)
                print(f"❌ Failed to process: {yaml_file} (exit code: {exit_code})")

        except Exception as e:
            failed_files.append(yaml_file)
            print(f"❌ Exception while processing {yaml_file}: {e}")

        print("-" * 50)
        print()

    # Print final summary
    print("📊 PROCESSING SUMMARY:")
    print(f"   Total files: {len(yaml_files)}")
    print(f"   Successful: {len(successful_files)}")
    print(f"   Failed: {len(failed_files)}")

    if successful_files:
        print(f"   ✅ Success: {', '.join(successful_files)}")

    if failed_files:
        print(f"   ❌ Failed: {', '.join(failed_files)}")

    # Return overall exit code
    return 0 if len(failed_files) == 0 else 1


if __name__ == "__main__":
    # Check if manual mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        manual_scrape()
    else:
        exit_code = process_yaml_list()
        sys.exit(exit_code)
