"""
Web driver management for Chrome browser automation.
Handles creating, configuring, and managing Chrome driver instances.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional


class WebDriverManager:
    """Manages Chrome WebDriver instances and browser interactions."""
    
    def __init__(self):
        self.driver = None
    
    def create_driver(self) -> Optional[webdriver.Chrome]:
        """
        Create a new Chrome driver instance.
        
        Returns:
            Chrome WebDriver instance or None if failed
        """
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return self.driver
        except Exception as e:
            print(f"❌ Failed to create Chrome driver: {e}")
            return None
    
    def navigate_to_url(self, url: str, wait_time: int = 3) -> bool:
        """
        Navigate to a URL and wait for page to load.
        
        Args:
            url: URL to navigate to
            wait_time: Additional wait time after page load
            
        Returns:
            True if navigation successful, False otherwise
        """
        if not self.driver:
            print("❌ No driver available for navigation")
            return False
        
        try:
            print(f"  📍 Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page load indicators
            success = self._wait_for_page_load(wait_time)
            if success:
                print(f"  ✅ Page loaded successfully")
            else:
                print(f"  ⚠️ Page load may be incomplete")
            
            return success
            
        except Exception as e:
            print(f"  ❌ Navigation failed: {e}")
            return False
    
    def _wait_for_page_load(self, additional_wait: int) -> bool:
        """
        Wait for page to fully load.
        
        Args:
            additional_wait: Additional wait time in seconds
            
        Returns:
            True if page loaded successfully
        """
        try:
            # Wait for body element
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for main container
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main.container"))
            )
            
            # Additional wait for dynamic content
            time.sleep(additional_wait + 1)
            
            return True
            
        except Exception as e:
            print(f"  ⚠️ Page load timeout: {e}")
            return False
    
    def get_page_source(self) -> str:
        """
        Get the current page's HTML source.
        
        Returns:
            HTML source code as string, empty if failed
        """
        if not self.driver:
            return ""
        
        try:
            return self.driver.page_source
        except Exception as e:
            print(f"  ❌ Failed to get page source: {e}")
            return ""
    
    def get_current_url(self) -> str:
        """
        Get the current page URL.
        
        Returns:
            Current URL as string, empty if failed
        """
        if not self.driver:
            return ""
        
        try:
            return self.driver.current_url
        except Exception as e:
            print(f"  ❌ Failed to get current URL: {e}")
            return ""
    
    def close_driver(self):
        """Close the driver and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                print("  🔒 Driver closed")
            except Exception as e:
                print(f"  ⚠️ Error closing driver: {e}")
    
    def is_on_cardmarket(self) -> bool:
        """
        Check if currently on a CardMarket page.
        
        Returns:
            True if on CardMarket, False otherwise
        """
        current_url = self.get_current_url()
        return 'cardmarket.com' in current_url if current_url else False
