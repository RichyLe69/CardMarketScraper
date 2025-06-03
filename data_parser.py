"""
Data parsing functionality for CardMarket listings.
Handles extracting and parsing card listing data from HTML.
"""

import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional


class DataParser:
    """Parses CardMarket listing data from HTML content."""
    
    def __init__(self):
        pass
    
    def parse_page_data(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse all listing data from HTML page content.
        
        Args:
            html_content: Raw HTML content from the page
            
        Returns:
            List of dictionaries containing listing data
        """
        if not html_content:
            print("    ❌ No HTML content provided")
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Navigate to the listings table
        table_body = self._find_listings_table(soup)
        if not table_body:
            return []
        
        # Find all product rows
        product_rows = self._find_product_rows(table_body)
        if not product_rows:
            print("    ❌ No product rows found")
            return []
        
        print(f"    🔍 Found {len(product_rows)} product rows")
        
        # Parse each row
        listings = []
        for i, row in enumerate(product_rows):
            listing = self._parse_single_row(row)
            if listing:
                listings.append(listing)
        
        print(f"    ✅ Successfully parsed {len(listings)} listings")
        return listings
    
    def _find_listings_table(self, soup: BeautifulSoup) -> Optional[Any]:
        """
        Navigate through HTML structure to find the listings table.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Table body element or None if not found
        """
        # Navigate through the expected HTML structure
        container = soup.find('main', class_='container')
        if not container:
            print("    ❌ No main container found")
            return None
        
        main_content = container.find('div', id='mainContent')
        if not main_content:
            print("    ❌ No mainContent found")
            return None
        
        table_section = main_content.find('section', id='table')
        if not table_section:
            print("    ❌ No table section found")
            return None
        
        table_div = table_section.find('div', class_='table article-table table-striped')
        if not table_div:
            print("    ❌ No table div found")
            return None
        
        table_body = table_div.find('div', class_='table-body')
        if not table_body:
            print("    ❌ No table body found")
            return None
        
        return table_body
    
    def _find_product_rows(self, table_body) -> List[Any]:
        """
        Find all product rows in the table body.
        
        Args:
            table_body: Table body element
            
        Returns:
            List of product row elements
        """
        return table_body.find_all('div', {'id': re.compile(r'articleRow\d+')})
    
    def _parse_single_row(self, row) -> Optional[Dict[str, Any]]:
        """
        Parse a single listing row and extract all data.
        
        Args:
            row: HTML element representing a single listing row
            
        Returns:
            Dictionary containing listing data or None if parsing failed
        """
        try:
            result = self._create_empty_listing()
            
            # Extract seller information
            self._extract_seller_info(row, result)
            
            # Extract product information
            self._extract_product_info(row, result)
            
            # Extract offer information (price and quantity)
            self._extract_offer_info(row, result)
            
            return result
            
        except Exception as e:
            print(f"    ⚠️ Error parsing row: {e}")
            return None
    
    def _create_empty_listing(self) -> Dict[str, Any]:
        """
        Create an empty listing dictionary with default values.
        
        Returns:
            Dictionary with default listing structure
        """
        return {
            'seller_username': '',
            'seller_sales_count': 0,
            'condition': '',
            'condition_badge': '',
            'language': '',
            'edition': '',
            'price': '',
            'quantity': 1
        }
    
    def _extract_seller_info(self, row, result: Dict[str, Any]):
        """
        Extract seller information from the row.
        
        Args:
            row: HTML row element
            result: Dictionary to store extracted data
        """
        seller_section = row.find('div', class_='col-seller col-12 col-lg-auto')
        if not seller_section:
            return
        
        seller_info_span = seller_section.find('span', class_='seller-info d-flex align-items-center')
        if not seller_info_span:
            return
        
        # Extract sales count
        self._extract_sales_count(seller_info_span, result)
        
        # Extract username
        self._extract_username(seller_info_span, result)
    
    def _extract_sales_count(self, seller_info_span, result: Dict[str, Any]):
        """Extract seller sales count."""
        sales_badges = seller_info_span.find_all('span', class_=re.compile(r'.*sell-count.*'))
        for badge in sales_badges:
            tooltip = badge.get('data-bs-original-title', '')
            text = badge.get_text(strip=True)
            
            for source in [tooltip, text]:
                if source:
                    sales_match = re.search(r'(\d+)', source)
                    if sales_match:
                        result['seller_sales_count'] = int(sales_match.group(1))
                        return
    
    def _extract_username(self, seller_info_span, result: Dict[str, Any]):
        """Extract seller username."""
        all_links = seller_info_span.find_all('a')
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Try to extract from URL
            if '/Users/' in href:
                username_match = re.search(r'/Users/([^/?]+)', href)
                if username_match:
                    result['seller_username'] = username_match.group(1)
                    return
            
            # Use link text as fallback
            if text and len(text) > 2:
                result['seller_username'] = text
                return
    
    def _extract_product_info(self, row, result: Dict[str, Any]):
        """
        Extract product information from the row.
        
        Args:
            row: HTML row element
            result: Dictionary to store extracted data
        """
        product_section = row.find('div', class_='col-product col-12 col-lg')
        if not product_section:
            return
        
        attributes_section = product_section.find('div', class_='product-attributes col')
        if not attributes_section:
            return
        
        # Extract condition
        self._extract_condition(attributes_section, result)
        
        # Extract language
        self._extract_language(attributes_section, result)
        
        # Extract edition
        self._extract_edition(attributes_section, result)
    
    def _extract_condition(self, attributes_section, result: Dict[str, Any]):
        """Extract card condition information."""
        condition_elements = attributes_section.find_all(attrs={'data-bs-original-title': True})
        for elem in condition_elements:
            title = elem.get('data-bs-original-title', '')
            text = elem.get_text(strip=True)
            
            if any(word in title.lower() for word in ['mint', 'played', 'damaged', 'excellent', 'good', 'poor']):
                result['condition'] = title
                result['condition_badge'] = text
                return
    
    def _extract_language(self, attributes_section, result: Dict[str, Any]):
        """Extract card language information."""
        language_elements = attributes_section.find_all(attrs={'aria-label': True})
        for elem in language_elements:
            aria_label = elem.get('aria-label', '')
            data_title = elem.get('data-bs-original-title', '')
            
            if aria_label and len(aria_label) > 2:
                result['language'] = aria_label
                return
            elif (data_title and len(data_title) > 2 and 
                  not any(word in data_title.lower() for word in ['mint', 'played', 'damaged'])):
                result['language'] = data_title
                return
    
    def _extract_edition(self, attributes_section, result: Dict[str, Any]):
        """Extract card edition information (1st edition only)."""
        # Check data-bs-original-title attributes
        edition_elements = attributes_section.find_all(attrs={'data-bs-original-title': True})
        for elem in edition_elements:
            title = elem.get('data-bs-original-title', '')
            aria_label = elem.get('aria-label', '')
            
            if 'first edition' in title.lower() or 'first edition' in aria_label.lower():
                result['edition'] = '1st'
                return
        
        # Check onmouseover attributes
        first_ed_spans = attributes_section.find_all('span', attrs={'onmouseover': True})
        for span in first_ed_spans:
            onmouseover = span.get('onmouseover', '')
            if 'first edition' in onmouseover.lower():
                result['edition'] = '1st'
                return
    
    def _extract_offer_info(self, row, result: Dict[str, Any]):
        """
        Extract offer information (price and quantity) from the row.
        
        Args:
            row: HTML row element
            result: Dictionary to store extracted data
        """
        offer_section = row.find('div', class_='col-offer col-auto')
        if not offer_section:
            return
        
        # Extract price
        self._extract_price(offer_section, result)
        
        # Extract quantity
        self._extract_quantity(offer_section, result)
    
    def _extract_price(self, offer_section, result: Dict[str, Any]):
        """Extract price information."""
        price_span = offer_section.find('span', class_='color-primary small text-end text-nowrap fw-bold')
        if price_span:
            price_text = price_span.get_text(strip=True)
            price_match = re.search(r'([\d,\.]+)', price_text)
            if price_match:
                result['price'] = price_match.group(1)
            else:
                result['price'] = price_text.replace('€', '').strip()
    
    def _extract_quantity(self, offer_section, result: Dict[str, Any]):
        """Extract quantity information."""
        quantity_container = offer_section.find('div', class_='amount-container d-none d-md-flex justify-content-end me-3')
        if quantity_container:
            item_count_span = quantity_container.find('span', class_='item-count small text-end')
            if item_count_span:
                quantity_text = item_count_span.get_text(strip=True)
                quantity_match = re.search(r'(\d+)', quantity_text)
                if quantity_match:
                    result['quantity'] = int(quantity_match.group(1))
