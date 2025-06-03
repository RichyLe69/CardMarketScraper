import pandas as pd
import numpy as np
import os
from pathlib import Path
import re
from typing import Dict, List, Tuple, Any
from difflib import SequenceMatcher
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class CardPriceAnalyzer:
    def __init__(self, base_path: str = "/output"):
        """
        Initialize the Card Price Analyzer

        Args:
            base_path (str): Base directory containing date folders with Excel files
        """
        self.base_path = Path(base_path)
        self.languages = ['English', 'German', 'Spanish', 'French', 'Italian']
        self.foreign_languages = [lang for lang in self.languages if lang != 'English']

    def parse_euro_price(self, price_str: str) -> float:
        """
        Convert euro price string to float

        Args:
            price_str: Price string like "265,00" or "1.234,56"

        Returns:
            float: Price as decimal number
        """
        if pd.isna(price_str) or price_str == '':
            return 0.0

        # Convert to string and clean
        price_str = str(price_str).strip()

        # Handle European number format (comma as decimal separator)
        # Remove any currency symbols
        price_str = re.sub(r'[€$£]', '', price_str)

        # If there's both dot and comma, dot is thousands separator
        if '.' in price_str and ',' in price_str:
            price_str = price_str.replace('.', '')
            price_str = price_str.replace(',', '.')
        elif ',' in price_str:
            # Only comma - it's the decimal separator
            price_str = price_str.replace(',', '.')

        try:
            return float(price_str)
        except ValueError:
            return 0.0

    def analyze_card_data(self, df: pd.DataFrame, card_name: str) -> Dict[str, Any]:
        """
        Analyze individual card data from a DataFrame

        Args:
            df: DataFrame with card data
            card_name: Name of the card

        Returns:
            Dict containing analysis results
        """
        # Debug: Print sheet structure
        print(f"\n--- Debugging sheet: {card_name} ---")
        print(f"Sheet shape: {df.shape}")

        # Skip header rows and get actual data
        if len(df) < 5:
            print(f"Sheet too small (less than 5 rows), skipping {card_name}")
            return self._empty_card_analysis(card_name)

        # Row 4 contains headers (index 3), data starts from row 5 (index 4)
        # First, get the headers from row 4 (index 2)
        header_row = df.iloc[2].tolist()  # Row 4 (index 3) - the actual headers
        print(f"Headers from row 4 (index 3): {header_row}")

        # Data starts from row 5 (index 3)
        data_df = df.iloc[3:].copy()  # Skip first 4 rows (0,1,2,3) to get data from row 5+
        data_df.columns = header_row  # Set the proper column names from row 4

        print(f"Data after setting proper headers (shape: {data_df.shape}):")
        print(data_df.head())

        # Clean column names
        data_df.columns = [str(col).strip() if pd.notna(col) else f'col_{i}' for i, col in enumerate(data_df.columns)]

        # Find relevant columns (case insensitive)
        language_col = None
        price_col = None
        quantity_col = None

        print("Looking for columns containing:")
        for col in data_df.columns:
            col_lower = str(col).lower()
            print(f"  '{col}' -> '{col_lower}'")
            if 'language' in col_lower:
                language_col = col
                print(f"    Found LANGUAGE column: {col}")
            elif 'price' in col_lower:
                price_col = col
                print(f"    Found PRICE column: {col}")
            elif 'quantity' in col_lower:
                quantity_col = col
                print(f"    Found QUANTITY column: {col}")

        print(f"Final column mapping: Language={language_col}, Price={price_col}, Quantity={quantity_col}")

        if not all([language_col, price_col, quantity_col]):
            print(f"Missing required columns for {card_name}")
            return self._empty_card_analysis(card_name)

        # Clean the data
        data_df = data_df.dropna(subset=[language_col, price_col, quantity_col])

        # Convert prices
        data_df['price_numeric'] = data_df[price_col].apply(self.parse_euro_price)

        # Convert quantities
        data_df['quantity_numeric'] = pd.to_numeric(data_df[quantity_col], errors='coerce').fillna(0)

        # Filter out zero quantities and prices
        data_df = data_df[(data_df['quantity_numeric'] > 0) & (data_df['price_numeric'] > 0)]

        if len(data_df) == 0:
            return self._empty_card_analysis(card_name)

        # Analyze by language
        results = {
            'card_name': card_name,
            'total_listings': len(data_df),
            'languages': {},
            'foreign_combined': {}
        }

        # Process each language
        for language in self.languages:
            lang_data = data_df[data_df[language_col].str.contains(language, case=False, na=False)]
            if len(lang_data) > 0:
                results['languages'][language] = self._calculate_stats(lang_data)

        # Process foreign (non-English) combined
        foreign_data = data_df[~data_df[language_col].str.contains('English', case=False, na=False)]
        if len(foreign_data) > 0:
            results['foreign_combined'] = self._calculate_stats(foreign_data)

        return results

    def _calculate_stats(self, data_df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate statistics for a subset of data"""
        prices = data_df['price_numeric']
        quantities = data_df['quantity_numeric']

        return {
            'total_quantity': int(quantities.sum()),
            'total_listings': len(data_df),
            'price_min': float(prices.min()),
            'price_max': float(prices.max()),
            'price_mean': float(prices.mean()),
            'price_median': float(prices.median()),
            'avg_quantity_per_listing': float(quantities.mean())
        }

    def _empty_card_analysis(self, card_name: str) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'card_name': card_name,
            'total_listings': 0,
            'languages': {},
            'foreign_combined': {}
        }

    def analyze_excel_file(self, excel_path: Path) -> Dict[str, Any]:
        """
        Analyze a single Excel file (card list)

        Args:
            excel_path: Path to Excel file

        Returns:
            Dict containing analysis of all cards in the file
        """
        try:
            # Get all sheet names
            excel_file = pd.ExcelFile(excel_path)
            sheet_names = excel_file.sheet_names

            list_results = {
                'file_name': excel_path.name,
                'file_path': str(excel_path),
                'total_cards': len(sheet_names),
                'cards': {},
                'list_summary': {}
            }

            # Analyze each sheet (card)
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                    card_analysis = self.analyze_card_data(df, sheet_name)
                    list_results['cards'][sheet_name] = card_analysis
                except Exception as e:
                    print(f"Error analyzing sheet {sheet_name} in {excel_path.name}: {e}")
                    list_results['cards'][sheet_name] = self._empty_card_analysis(sheet_name)

            # Calculate list summary
            list_results['list_summary'] = self._calculate_list_summary(list_results['cards'])

            return list_results

        except Exception as e:
            print(f"Error analyzing Excel file {excel_path}: {e}")
            return {
                'file_name': excel_path.name,
                'file_path': str(excel_path),
                'total_cards': 0,
                'cards': {},
                'list_summary': {},
                'error': str(e)
            }

    def _calculate_list_summary(self, cards_data: Dict) -> Dict[str, Any]:
        """Calculate summary statistics for entire list"""
        summary = {
            'total_cards_with_data': 0,
            'languages': {},
            'foreign_combined': {}
        }

        # Initialize language totals
        for language in self.languages:
            summary['languages'][language] = {
                'total_quantity': 0,
                'total_listings': 0,
                'cards_available': 0,
                'price_min': float('inf'),
                'price_max': 0,
                'all_prices': []
            }

        summary['foreign_combined'] = {
            'total_quantity': 0,
            'total_listings': 0,
            'cards_available': 0,
            'price_min': float('inf'),
            'price_max': 0,
            'all_prices': []
        }

        # Aggregate data from all cards
        for card_name, card_data in cards_data.items():
            if card_data['total_listings'] > 0:
                summary['total_cards_with_data'] += 1

                # Process each language
                for language in self.languages:
                    if language in card_data['languages']:
                        lang_data = card_data['languages'][language]
                        lang_summary = summary['languages'][language]

                        lang_summary['total_quantity'] += lang_data['total_quantity']
                        lang_summary['total_listings'] += lang_data['total_listings']
                        lang_summary['cards_available'] += 1
                        lang_summary['price_min'] = min(lang_summary['price_min'], lang_data['price_min'])
                        lang_summary['price_max'] = max(lang_summary['price_max'], lang_data['price_max'])
                        lang_summary['all_prices'].extend([lang_data['price_min'], lang_data['price_max']])

                # Process foreign combined
                if 'foreign_combined' in card_data and card_data['foreign_combined']:
                    foreign_data = card_data['foreign_combined']
                    foreign_summary = summary['foreign_combined']

                    foreign_summary['total_quantity'] += foreign_data['total_quantity']
                    foreign_summary['total_listings'] += foreign_data['total_listings']
                    foreign_summary['cards_available'] += 1
                    foreign_summary['price_min'] = min(foreign_summary['price_min'], foreign_data['price_min'])
                    foreign_summary['price_max'] = max(foreign_summary['price_max'], foreign_data['price_max'])
                    foreign_summary['all_prices'].extend([foreign_data['price_min'], foreign_data['price_max']])

        # Calculate final statistics
        for lang_key in ['languages', 'foreign_combined']:
            if lang_key == 'languages':
                lang_dict = summary['languages']
            else:
                lang_dict = {'foreign_combined': summary['foreign_combined']}

            for lang_name, lang_data in lang_dict.items():
                if lang_data['all_prices']:
                    lang_data['price_mean'] = np.mean(lang_data['all_prices'])
                    lang_data['price_median'] = np.median(lang_data['all_prices'])
                else:
                    lang_data['price_min'] = 0
                    lang_data['price_mean'] = 0
                    lang_data['price_median'] = 0

                # Clean up temporary data
                del lang_data['all_prices']

        return summary

    def analyze_date_folder(self, date_folder: str) -> Dict[str, Any]:
        """
        Analyze all Excel files in a date folder

        Args:
            date_folder: Date folder name (e.g., "2024-01-15")

        Returns:
            Dict containing analysis of all Excel files in the folder
        """
        folder_path = self.base_path / date_folder

        if not folder_path.exists():
            return {'error': f'Date folder {date_folder} not found'}

        excel_files = list(folder_path.glob('*.xlsx'))

        if not excel_files:
            return {'error': f'No Excel files found in {date_folder}'}

        results = {
            'date_folder': date_folder,
            'total_excel_files': len(excel_files),
            'files': {}
        }

        for excel_file in excel_files:
            print(f"Analyzing {excel_file.name}...")
            file_results = self.analyze_excel_file(excel_file)
            results['files'][excel_file.name] = file_results

        return results

    def print_analysis_summary(self, analysis_results: Dict):
        """Print a readable summary of analysis results"""
        if 'error' in analysis_results:
            print(f"Error: {analysis_results['error']}")
            return

        print(f"\n=== Analysis Results for {analysis_results['date_folder']} ===")
        print(f"Total Excel files analyzed: {analysis_results['total_excel_files']}")

        for file_name, file_data in analysis_results['files'].items():
            print(f"\n--- {file_name} ---")
            print(f"Total cards: {file_data['total_cards']}")

            if 'list_summary' in file_data:
                summary = file_data['list_summary']
                print(f"Cards with data: {summary['total_cards_with_data']}")

                # Print language summaries
                for language in self.languages:
                    if language in summary['languages'] and summary['languages'][language]['cards_available'] > 0:
                        lang_data = summary['languages'][language]
                        print(f"  {language}: {lang_data['cards_available']} cards, "
                              f"€{lang_data['price_min']:.2f}-€{lang_data['price_max']:.2f} "
                              f"(avg: €{lang_data['price_mean']:.2f})")

                if summary['foreign_combined']['cards_available'] > 0:
                    foreign_data = summary['foreign_combined']
                    print(f"  Foreign Combined: {foreign_data['cards_available']} cards, "
                          f"€{foreign_data['price_min']:.2f}-€{foreign_data['price_max']:.2f} "
                          f"(avg: €{foreign_data['price_mean']:.2f})")


def save_analysis_to_file(analysis_results: Dict, output_path: Path):
    """Save analysis results to a text file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        if 'error' in analysis_results:
            f.write(f"Error: {analysis_results['error']}\n")
            return

        f.write(f"=== Card Price Analysis Results ===\n")
        f.write(f"Date Folder: {analysis_results['date_folder']}\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Excel files analyzed: {analysis_results['total_excel_files']}\n\n")

        for file_name, file_data in analysis_results['files'].items():
            f.write(f"{'=' * 60}\n")
            f.write(f"FILE: {file_name}\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Total cards in file: {file_data['total_cards']}\n")

            if 'error' in file_data:
                f.write(f"Error processing file: {file_data['error']}\n\n")
                continue

            # Write list summary
            if 'list_summary' in file_data:
                summary = file_data['list_summary']
                f.write(f"Cards with pricing data: {summary['total_cards_with_data']}\n\n")

                f.write("LIST SUMMARY BY LANGUAGE:\n")
                f.write("-" * 40 + "\n")

                # Write language summaries
                languages = ['English', 'German', 'Spanish', 'French', 'Italian']
                for language in languages:
                    if language in summary['languages'] and summary['languages'][language]['cards_available'] > 0:
                        lang_data = summary['languages'][language]
                        f.write(f"{language}:\n")
                        f.write(f"  Cards available: {lang_data['cards_available']}\n")
                        f.write(f"  Total quantity: {lang_data['total_quantity']}\n")
                        f.write(f"  Total listings: {lang_data['total_listings']}\n")
                        f.write(f"  Price range: €{lang_data['price_min']:.2f} - €{lang_data['price_max']:.2f}\n")
                        f.write(f"  Average price: €{lang_data['price_mean']:.2f}\n")
                        f.write(f"  Median price: €{lang_data['price_median']:.2f}\n\n")

                # Foreign combined summary
                if summary['foreign_combined']['cards_available'] > 0:
                    foreign_data = summary['foreign_combined']
                    f.write("FOREIGN LANGUAGES COMBINED:\n")
                    f.write(f"  Cards available: {foreign_data['cards_available']}\n")
                    f.write(f"  Total quantity: {foreign_data['total_quantity']}\n")
                    f.write(f"  Total listings: {foreign_data['total_listings']}\n")
                    f.write(f"  Price range: €{foreign_data['price_min']:.2f} - €{foreign_data['price_max']:.2f}\n")
                    f.write(f"  Average price: €{foreign_data['price_mean']:.2f}\n")
                    f.write(f"  Median price: €{foreign_data['price_median']:.2f}\n\n")

            # Write individual card details
            f.write("INDIVIDUAL CARD DETAILS:\n")
            f.write("-" * 40 + "\n")

            for card_name, card_data in file_data.get('cards', {}).items():
                f.write(f"\nCard: {card_name}\n")
                if card_data['total_listings'] == 0:
                    f.write("  No pricing data available\n")
                    continue

                f.write(f"  Total listings: {card_data['total_listings']}\n")

                # Individual languages
                for language in languages:
                    if language in card_data.get('languages', {}):
                        lang_data = card_data['languages'][language]
                        f.write(f"  {language}:\n")
                        f.write(f"    Quantity: {lang_data['total_quantity']}\n")
                        f.write(f"    Listings: {lang_data['total_listings']}\n")
                        f.write(f"    Price: €{lang_data['price_min']:.2f} - €{lang_data['price_max']:.2f} "
                                f"(avg: €{lang_data['price_mean']:.2f}, median: €{lang_data['price_median']:.2f})\n")

                # Foreign combined for this card
                if 'foreign_combined' in card_data and card_data['foreign_combined']:
                    foreign_data = card_data['foreign_combined']
                    f.write(f"  Foreign Combined:\n")
                    f.write(f"    Quantity: {foreign_data['total_quantity']}\n")
                    f.write(f"    Listings: {foreign_data['total_listings']}\n")
                    f.write(f"    Price: €{foreign_data['price_min']:.2f} - €{foreign_data['price_max']:.2f} "
                            f"(avg: €{foreign_data['price_mean']:.2f}, median: €{foreign_data['price_median']:.2f})\n")

            f.write("\n")


def main():
    """Main function to analyze today's Excel files and save results"""
    from datetime import datetime
    import sys

    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Starting analysis for date: {today}")

    # Get current working directory and set up paths relative to project
    current_dir = Path.cwd()
    project_output_dir = current_dir / "output"
    project_analysis_dir = current_dir / "output_analysis"

    print(f"Looking for Excel files in: {project_output_dir / today}")
    print(f"Current working directory: {current_dir}")

    # Initialize analyzer with relative path
    analyzer = CardPriceAnalyzer(str(project_output_dir))

    # Create output directory
    output_date_folder = project_analysis_dir / today
    output_date_folder.mkdir(parents=True, exist_ok=True)

    print(f"Output will be saved to: {output_date_folder}")

    # Analyze today's folder
    print(f"Analyzing Excel files in /output/{today}/...")
    results = analyzer.analyze_date_folder(today)

    if 'error' in results:
        print(f"Error: {results['error']}")

        # Save error to file
        error_file = output_date_folder / "analysis_error.txt"
        with open(error_file, 'w') as f:
            f.write(f"Analysis Error for {today}\n")
            f.write(f"Error: {results['error']}\n")
            f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"Error details saved to: {error_file}")
        return

    # Save overall summary
    summary_file = output_date_folder / f"summary_{today}.txt"
    save_analysis_to_file(results, summary_file)
    print(f"Overall summary saved to: {summary_file}")

    # Save individual file analyses
    for file_name, file_data in results['files'].items():
        # Clean filename for use in path
        clean_filename = re.sub(r'[^\w\-_.]', '_', file_name.replace('.xlsx', ''))
        individual_file = output_date_folder / f"detailed_{clean_filename}.txt"

        # Create individual file analysis
        individual_results = {
            'date_folder': results['date_folder'],
            'total_excel_files': 1,
            'files': {file_name: file_data}
        }

        save_analysis_to_file(individual_results, individual_file)
        print(f"Detailed analysis for {file_name} saved to: {individual_file}")

    # Print console summary
    print(f"\n{'=' * 60}")
    print("ANALYSIS COMPLETE")
    print(f"{'=' * 60}")
    analyzer.print_analysis_summary(results)

    print(f"\n{'=' * 60}")
    print("FILES CREATED:")
    print(f"{'=' * 60}")
    print(f"Summary: {summary_file}")
    for file_name in results['files'].keys():
        clean_filename = re.sub(r'[^\w\-_.]', '_', file_name.replace('.xlsx', ''))
        print(f"Details: {output_date_folder / f'detailed_{clean_filename}.txt'}")

    print(f"\nAll analysis files saved to: {output_date_folder}")


if __name__ == "__main__":
    main()
