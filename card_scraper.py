"""
Main scraper class that coordinates all scraping operations.
Handles the sequential scraping of individual cards.
"""

import time
from typing import Dict, Any, List, Tuple
from collections import OrderedDict

from config_manager import ConfigManager
from url_builder import URLBuilder
from web_driver_manager import WebDriverManager
from data_parser import DataParser
from excel_exporter import ExcelExporter


class CardScraper:
    """Main scraper that coordinates all scraping operations."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.url_builder = URLBuilder()
        self.web_driver = WebDriverManager()
        self.data_parser = DataParser()
        self.excel_exporter = ExcelExporter()
    
    def scrape_cards_from_config(self, config_file: str) -> bool:
        """
        Main method to scrape cards based on configuration file.
        
        Args:
            config_file: Path to YAML configuration file
            
        Returns:
            True if scraping completed successfully, False otherwise
        """
        # Load and validate configuration
        config = self.config_manager.load_config(config_file)
        if not config or not self.config_manager.validate_config(config):
            return False
        
        # Extract configuration data
        list_name = self.config_manager.get_list_name(config)
        cards = self.config_manager.get_cards(config)
        wait_time = self.config_manager.get_wait_time(config)
        
        print(f"📋 List: {list_name}")
        print(f"🃏 Cards to scrape: {len(cards)}")
        print(f"⏱️ Wait time per card: {wait_time} seconds")
        
        # Initialize web driver
        if not self.web_driver.create_driver():
            print("❌ Failed to initialize web driver")
            return False
        
        try:
            # Scrape all cards sequentially
            scraped_data = self._scrape_all_cards(cards, wait_time)
            
            # Export to Excel
            success = self.excel_exporter.save_to_excel(scraped_data, list_name)
            if success:
                self.excel_exporter.print_summary(scraped_data)
                print(f"\n🎉 Scraping completed successfully!")
            
            return success
            
        finally:
            # Always clean up the web driver
            self.web_driver.close_driver()
    
    def _scrape_all_cards(self, cards: Dict[str, Any], wait_time: int) -> Dict[str, Dict[str, Any]]:
        """
        Scrape all cards sequentially.
        
        Args:
            cards: Dictionary of card names and configurations
            wait_time: Wait time between requests
            
        Returns:
            Dictionary containing all scraped data organized by sheet name
        """
        scraped_data = OrderedDict()
        total_cards = len(cards)
        
        print(f"\n🚀 Starting sequential scraping...")
        start_time = time.time()
        
        for i, (card_name, card_config) in enumerate(cards.items(), 1):
            print(f"\n🔄 [{i}/{total_cards}] Processing: {card_name}")
            
            # Scrape individual card
            listings = self._scrape_single_card(card_name, card_config, wait_time, i)
            
            # Prepare data for export
            url = self.url_builder.build_url(card_name, card_config)
            sheet_name = self.excel_exporter.clean_sheet_name(card_name)
            scraped_data[sheet_name] = {
                'listings': listings,
                'url': url
            }
            
            # Progress update
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = total_cards - i
            eta = remaining * avg_time
            
            print(f"📊 Progress: {i}/{total_cards} ({i/total_cards*100:.1f}%) - ETA: {eta:.1f}s")
        
        elapsed_total = time.time() - start_time
        print(f"\n⏱️ Total time: {elapsed_total:.1f}s (avg: {elapsed_total/total_cards:.1f}s per card)")
        
        return scraped_data
    
    def _scrape_single_card(self, card_name: str, card_config: Dict[str, Any], 
                           wait_time: int, card_number: int) -> List[Dict[str, Any]]:
        """
        Scrape a single card and return its listings.
        
        Args:
            card_name: Name of the card to scrape
            card_config: Configuration for the card
            wait_time: Wait time for page loading
            card_number: Card number for logging
            
        Returns:
            List of listing dictionaries
        """
        try:
            # Build URL for the card
            url = self.url_builder.build_url(card_name, card_config)
            
            # Navigate to the page
            if not self.web_driver.navigate_to_url(url, wait_time):
                print(f"  ❌ [{card_number}] Failed to navigate to page")
                return []
            
            # Verify we're on the right page
            if not self.web_driver.is_on_cardmarket():
                current_url = self.web_driver.get_current_url()
                print(f"  ⚠️ [{card_number}] Not on CardMarket page: {current_url}")
                return []
            
            # Get page source and parse data
            html_content = self.web_driver.get_page_source()
            if not html_content:
                print(f"  ❌ [{card_number}] Failed to get page content")
                return []
            
            print(f"  ✅ [{card_number}] Page loaded, extracting data...")
            listings = self.data_parser.parse_page_data(html_content)
            
            print(f"✅ [{card_number}] Completed: {card_name} ({len(listings)} listings)")
            return listings
            
        except Exception as e:
            print(f"❌ [{card_number}] Error scraping {card_name}: {e}")
            return []
    
    def scrape_single_url(self, url: str, card_name: str = "Manual", 
                         wait_time: int = 3) -> List[Dict[str, Any]]:
        """
        Scrape a single URL manually (useful for testing).
        
        Args:
            url: Direct URL to scrape
            card_name: Name for identification
            wait_time: Wait time for page loading
            
        Returns:
            List of listing dictionaries
        """
        print(f"🔄 Manual scraping: {card_name}")
        print(f"📍 URL: {url}")
        
        # Initialize web driver if not already done
        if not self.web_driver.driver:
            if not self.web_driver.create_driver():
                print("❌ Failed to initialize web driver")
                return []
        
        try:
            # Navigate and scrape
            if not self.web_driver.navigate_to_url(url, wait_time):
                print("❌ Failed to navigate to URL")
                return []
            
            html_content = self.web_driver.get_page_source()
            if not html_content:
                print("❌ Failed to get page content")
                return []
            
            listings = self.data_parser.parse_page_data(html_content)
            print(f"✅ Manual scraping completed: {len(listings)} listings found")
            
            return listings
            
        except Exception as e:
            print(f"❌ Error in manual scraping: {e}")
            return []
        
        finally:
            # Close driver after manual scraping
            self.web_driver.close_driver()
