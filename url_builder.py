"""
URL building functionality for CardMarket searches.
Handles constructing URLs with proper parameters and filters.
"""

from typing import Dict, Any, List


class URLBuilder:
    """Builds CardMarket URLs based on card configuration."""
    
    BASE_URL = "https://www.cardmarket.com/en/YuGiOh/Products/Singles/"
    
    def __init__(self):
        pass
    
    def build_url(self, card_name: str, card_config: Dict[str, Any]) -> str:
        """
        Build the complete URL for a card based on its configuration.
        
        Args:
            card_name: Name of the card
            card_config: Configuration dictionary for the card
            
        Returns:
            Complete URL string for the card search
        """
        url = self._build_base_url(card_name, card_config)
        params = self._build_parameters(card_config)
        
        if params:
            url += '?' + '&'.join(params)
        
        return url
    
    def _build_base_url(self, card_name: str, card_config: Dict[str, Any]) -> str:
        """
        Build the base URL with card name and set.
        
        Args:
            card_name: Name of the card
            card_config: Configuration dictionary for the card
            
        Returns:
            Base URL string
        """
        url = self.BASE_URL
        
        set_name = card_config.get('set', '')
        if set_name:
            url += f"{set_name}/{card_name}"
        else:
            url += card_name
        
        return url
    
    def _build_parameters(self, card_config: Dict[str, Any]) -> List[str]:
        """
        Build URL parameters based on card configuration.
        
        Args:
            card_config: Configuration dictionary for the card
            
        Returns:
            List of parameter strings
        """
        params = []
        
        # Add condition parameter
        condition_param = self._get_condition_parameter(card_config)
        if condition_param:
            params.append(condition_param)
        
        # Add edition parameter
        edition_param = self._get_edition_parameter(card_config)
        if edition_param:
            params.append(edition_param)
        
        return params
    
    def _get_condition_parameter(self, card_config: Dict[str, Any]) -> str:
        """
        Get condition parameter string.
        
        Args:
            card_config: Configuration dictionary for the card
            
        Returns:
            Condition parameter string or empty string
        """
        if 'condition' not in card_config:
            return ""
        
        condition = card_config['condition'].lower()
        if condition == 'near mint':
            return 'minCondition=2'
        
        return ""
    
    def _get_edition_parameter(self, card_config: Dict[str, Any]) -> str:
        """
        Get edition parameter string.
        
        Args:
            card_config: Configuration dictionary for the card
            
        Returns:
            Edition parameter string or empty string
        """
        if 'edition' not in card_config:
            return ""
        
        edition = card_config['edition'].lower()
        if edition == '1st':
            return 'isFirstEd=Y'
        
        return ""
