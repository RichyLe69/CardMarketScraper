import pandas as pd
import numpy as np
import os
import yaml
from pathlib import Path
import re
from typing import Dict, List, Tuple, Any
from difflib import SequenceMatcher
from datetime import datetime
import warnings

from card_price_analyzer import CardPriceAnalyzer


class DeckPriceEstimator:
    def __init__(self, base_output_path: str = "./output", decks_folder: str = "./decks"):
        """
        Initialize the Deck Price Estimator

        Args:
            base_output_path: Path to the output directory containing Excel analysis data
            decks_folder: Path to folder containing deck YAML files
        """
        self.analyzer = CardPriceAnalyzer(base_output_path)
        self.decks_folder = Path(decks_folder)
        self.decks_folder.mkdir(exist_ok=True)

    def list_available_decks(self) -> List[str]:
        """
        List all available deck YAML files in the decks folder

        Returns:
            List of deck file names (without .yaml extension)
        """
        yaml_files = list(self.decks_folder.glob("*.yaml")) + list(self.decks_folder.glob("*.yml"))
        return [f.stem for f in yaml_files]

    def select_deck_interactive(self) -> str:
        """
        Interactive deck selection menu

        Returns:
            Path to selected deck YAML file
        """
        available_decks = self.list_available_decks()

        if not available_decks:
            print("❌ No deck YAML files found in the decks folder.")
            print(f"📁 Decks folder: {self.decks_folder.absolute()}")

            # Offer to create example deck
            create_example = input("Would you like to create an example deck? (y/n): ").strip().lower()
            if create_example in ['y', 'yes']:
                example_path = self.create_example_deck_yaml()
                return example_path
            else:
                return ""

        print(f"\n📋 Available decks in {self.decks_folder}:")
        print("-" * 40)

        for i, deck_name in enumerate(available_decks, 1):
            # Try to get deck info from YAML
            deck_path = self.decks_folder / f"{deck_name}.yaml"
            if not deck_path.exists():
                deck_path = self.decks_folder / f"{deck_name}.yml"

            try:
                with open(deck_path, 'r', encoding='utf-8') as f:
                    deck_data = yaml.safe_load(f)
                    deck_display_name = deck_data.get('deck_name', deck_name)
                    deck_format = deck_data.get('format', 'Unknown format')
                    total_cards = sum(sum(category.values()) for category in deck_data.get('cards', {}).values())

                    print(f"{i:2d}. {deck_display_name}")
                    print(f"     Format: {deck_format} | Cards: {total_cards}")
            except:
                print(f"{i:2d}. {deck_name}")
                print(f"     (Error reading deck info)")

        print(f"{len(available_decks) + 1:2d}. Create new example deck")
        print(" 0. Exit")

        while True:
            try:
                choice = input(f"\nSelect deck (1-{len(available_decks) + 1}, 0 to exit): ").strip()

                if choice == '0':
                    return ""
                elif choice == str(len(available_decks) + 1):
                    return self.create_example_deck_yaml()
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(available_decks):
                        selected_deck = available_decks[choice_num - 1]
                        deck_path = self.decks_folder / f"{selected_deck}.yaml"
                        if not deck_path.exists():
                            deck_path = self.decks_folder / f"{selected_deck}.yml"
                        return str(deck_path)
                    else:
                        print(f"❌ Please enter a number between 0 and {len(available_decks) + 1}")
            except ValueError:
                print("❌ Please enter a valid number")

    def load_deck_from_yaml(self, yaml_path: str) -> Dict[str, Dict[str, int]]:
        """
        Load deck list from YAML file

        Args:
            yaml_path: Path to YAML file containing deck list

        Returns:
            Dict with deck structure
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as file:
                deck_data = yaml.safe_load(file)

            print(f"✓ Loaded deck from {yaml_path}")
            return deck_data
        except FileNotFoundError:
            print(f"❌ YAML file not found: {yaml_path}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML: {e}")
            return {}

    def create_example_deck_yaml(self) -> str:
        """Create an example deck YAML file in the decks folder"""
        examples = [
            {
                'filename': 'teledad_2009.yaml',
                'deck': {
                    'deck_name': 'Teledad 2009',
                    'format': 'March 2009',
                    'description': 'Classic Teleport Dark Armed Dragon deck',
                    'cards': {
                        'Monsters': {
                            'Dark Armed Dragon': 2,
                            'Caius the Shadow Monarch': 1,
                            'Plaguespreader Zombie': 1,
                            'Sangan': 1,
                            'Elemental Hero Stratos': 1,
                            'Destiny Hero - Malicious': 2
                        },
                        'Spells': {
                            'Allure of Darkness': 3,
                            'Emergency Teleport': 3,
                            'Reinforcement of the Army': 1,
                            'Brain Control': 1,
                            'Heavy Storm': 1
                        },
                        'Traps': {
                            'Trap Dustshoot': 3,
                            'Mirror Force': 1,
                            'Torrential Tribute': 1,
                            'Solemn Judgment': 1
                        }
                    }
                }
            },
            {
                'filename': 'goat_control.yaml',
                'deck': {
                    'deck_name': 'Goat Control',
                    'format': 'April 2005',
                    'description': 'Classic Goat Control format deck',
                    'cards': {
                        'Monsters': {
                            'Scapegoat': 1,  # Actually a spell but keeping for example
                            'Magician of Faith': 1,
                            'Morphing Jar': 1,
                            'Sangan': 1,
                            'Sinister Serpent': 1
                        },
                        'Spells': {
                            'Pot of Greed': 1,
                            'Graceful Charity': 1,
                            'Delinquent Duo': 1,
                            'Heavy Storm': 1,
                            'Mystical Space Typhoon': 1,
                            'Premature Burial': 1,
                            'Snatch Steal': 1,
                            'Book of Moon': 1
                        },
                        'Traps': {
                            'Mirror Force': 1,
                            'Ring of Destruction': 1,
                            'Torrential Tribute': 1,
                            'Call of the Haunted': 1
                        }
                    }
                }
            }
        ]

        print(f"\n📝 Creating example deck files...")

        # Show available examples
        print("Available examples:")
        for i, example in enumerate(examples, 1):
            deck_name = example['deck']['deck_name']
            format_name = example['deck']['format']
            print(f"{i}. {deck_name} ({format_name})")

        print(f"{len(examples) + 1}. Create all examples")

        try:
            choice = input(f"Select example to create (1-{len(examples) + 1}): ").strip()
            choice_num = int(choice)

            if choice_num == len(examples) + 1:
                # Create all examples
                created_files = []
                for example in examples:
                    yaml_path = self.decks_folder / example['filename']
                    with open(yaml_path, 'w', encoding='utf-8') as f:
                        yaml.dump(example['deck'], f, default_flow_style=False, allow_unicode=True)
                    created_files.append(str(yaml_path))
                    print(f"✓ Created: {yaml_path}")

                print(f"\n✅ Created {len(created_files)} example decks")
                return created_files[0]  # Return first one

            elif 1 <= choice_num <= len(examples):
                # Create selected example
                selected_example = examples[choice_num - 1]
                yaml_path = self.decks_folder / selected_example['filename']

                with open(yaml_path, 'w', encoding='utf-8') as f:
                    yaml.dump(selected_example['deck'], f, default_flow_style=False, allow_unicode=True)

                print(f"✓ Created example deck: {yaml_path}")
                return str(yaml_path)
            else:
                print("❌ Invalid choice")
                return ""

        except ValueError:
            print("❌ Invalid input")
            return ""

    def estimate_deck_price(self, deck_list: Dict[str, Dict[str, int]], analysis_data: Dict,
                            language_preference: str = 'English', fallback_to_foreign: bool = True,
                            optimize_for_min_price: bool = True) -> Dict[str, Any]:
        """
        Estimate deck price based on analysis data with optimization for minimum prices

        Args:
            deck_list: Dict like {'Monsters': {'Card Name': quantity, ...}, ...}
            analysis_data: Results from analyze_date_folder
            language_preference: Preferred language for pricing
            fallback_to_foreign: Whether to use foreign prices if preferred language not available
            optimize_for_min_price: Whether to optimize for minimum prices when buying

        Returns:
            Dict with price estimation results
        """
        # Flatten all available cards from analysis data
        all_cards = {}
        for file_name, file_data in analysis_data.get('files', {}).items():
            for card_name, card_data in file_data.get('cards', {}).items():
                all_cards[card_name] = card_data

        available_card_names = list(all_cards.keys())

        estimation_results = {
            'deck_list': deck_list,
            'language_preference': language_preference,
            'fallback_to_foreign': fallback_to_foreign,
            'optimize_for_min_price': optimize_for_min_price,
            'categories': {},
            'total_estimation': {
                'min_price': 0,
                'max_price': 0,
                'mean_price': 0,
                'median_price': 0,
                'optimized_price': 0,  # Price if buying at minimum available prices
                'cards_found': 0,
                'cards_not_found': 0,
                'total_cards_needed': 0
            },
            'not_found_cards': [],
            'purchase_strategy': []  # Detailed buying strategy
        }

        total_cards_needed = sum(sum(cards.values()) for cards in deck_list.values())
        estimation_results['total_estimation']['total_cards_needed'] = total_cards_needed

        # Process each category
        for category, cards in deck_list.items():
            category_results = {
                'cards': {},
                'category_totals': {
                    'min_price': 0,
                    'max_price': 0,
                    'mean_price': 0,
                    'median_price': 0,
                    'optimized_price': 0
                }
            }

            for card_name, quantity in cards.items():
                # Find matching card
                match_result, similarity = self.find_card_match(card_name, available_card_names)

                if match_result:
                    card_data = all_cards[match_result]

                    # Debug: Show available language data for this card
                    if language_preference == 'Foreign':
                        available_langs = list(card_data.get('languages', {}).keys())
                        has_foreign_combined = bool(card_data.get('foreign_combined'))
                        print(f"  🔍 {card_name} -> {match_result}")
                        print(f"     Available languages: {available_langs}")
                        print(f"     Has foreign_combined: {has_foreign_combined}")

                    # Get pricing for preferred language
                    price_data = None
                    source_type = None

                    if language_preference == 'Foreign':
                        # For "Foreign" preference, use the foreign_combined data
                        if card_data.get('foreign_combined'):
                            price_data = card_data['foreign_combined']
                            source_type = 'foreign_combined'
                        elif fallback_to_foreign:
                            # If no foreign_combined, try individual foreign languages
                            foreign_langs = ['German', 'Spanish', 'French', 'Italian']
                            for lang in foreign_langs:
                                if lang in card_data.get('languages', {}):
                                    price_data = card_data['languages'][lang]
                                    source_type = lang
                                    print(f"     Using {lang} as foreign fallback")
                                    break
                    elif language_preference in card_data.get('languages', {}):
                        # Specific language (English, German, etc.)
                        price_data = card_data['languages'][language_preference]
                        source_type = language_preference
                    elif fallback_to_foreign and card_data.get('foreign_combined'):
                        # Fallback to foreign combined
                        price_data = card_data['foreign_combined']
                        source_type = 'foreign_combined'

                    if price_data:
                        # Simple approach: just use minimum price * quantity
                        # This assumes you can get all copies at the minimum price
                        optimized_unit_price = price_data['price_min']
                        optimized_total = optimized_unit_price * quantity
                        available_quantity = price_data.get('total_quantity', 0)
                        purchase_feasible = available_quantity >= quantity

                        card_estimation = {
                            'requested_name': card_name,
                            'matched_name': match_result,
                            'similarity': similarity,
                            'quantity_needed': quantity,
                            'source_type': source_type,
                            'unit_prices': price_data,
                            'total_prices': {
                                'min_total': price_data['price_min'] * quantity,
                                'max_total': price_data['price_max'] * quantity,
                                'mean_total': price_data['price_mean'] * quantity,
                                'median_total': price_data['price_median'] * quantity,
                                'optimized_total': optimized_total
                            },
                            'optimized_strategy': {
                                'unit_price': optimized_unit_price,
                                'total_price': optimized_total,
                                'purchase_feasible': purchase_feasible,
                                'available_quantity': available_quantity
                            }
                        }

                        category_results['cards'][card_name] = card_estimation

                        # Add to category totals
                        category_results['category_totals']['min_price'] += card_estimation['total_prices']['min_total']
                        category_results['category_totals']['max_price'] += card_estimation['total_prices']['max_total']
                        category_results['category_totals']['mean_price'] += card_estimation['total_prices'][
                            'mean_total']
                        category_results['category_totals']['median_price'] += card_estimation['total_prices'][
                            'median_total']
                        category_results['category_totals']['optimized_price'] += card_estimation['total_prices'][
                            'optimized_total']

                        # Add to purchase strategy
                        estimation_results['purchase_strategy'].append({
                            'category': category,
                            'card': card_name,
                            'matched_card': match_result,
                            'quantity': quantity,
                            'language': source_type,
                            'unit_price': optimized_unit_price,
                            'total_price': optimized_total,
                            'feasible': purchase_feasible,
                            'similarity': similarity
                        })

                        estimation_results['total_estimation']['cards_found'] += 1
                    else:
                        estimation_results['not_found_cards'].append({
                            'category': category,
                            'card_name': card_name,
                            'reason': f'No pricing data for {language_preference} or foreign languages'
                        })
                        estimation_results['total_estimation']['cards_not_found'] += 1
                else:
                    estimation_results['not_found_cards'].append({
                        'category': category,
                        'card_name': card_name,
                        'reason': 'No matching card found'
                    })
                    estimation_results['total_estimation']['cards_not_found'] += 1

            estimation_results['categories'][category] = category_results

        # Calculate total estimation
        for category_data in estimation_results['categories'].values():
            estimation_results['total_estimation']['min_price'] += category_data['category_totals']['min_price']
            estimation_results['total_estimation']['max_price'] += category_data['category_totals']['max_price']
            estimation_results['total_estimation']['mean_price'] += category_data['category_totals']['mean_price']
            estimation_results['total_estimation']['median_price'] += category_data['category_totals']['median_price']
            estimation_results['total_estimation']['optimized_price'] += category_data['category_totals'][
                'optimized_price']

        return estimation_results

    def find_card_match(self, target_card: str, available_cards: List[str], threshold: float = 0.6) -> Tuple[
        str, float]:
        """
        Find the best matching card name from available cards

        Args:
            target_card: Card name to search for
            available_cards: List of available card names
            threshold: Minimum similarity threshold

        Returns:
            Tuple of (best_match, similarity_score)
        """
        best_match = None
        best_score = 0

        target_clean = self._clean_card_name(target_card)

        for card in available_cards:
            card_clean = self._clean_card_name(card)

            # Calculate similarity
            similarity = SequenceMatcher(None, target_clean.lower(), card_clean.lower()).ratio()

            # Also check if target is contained in card name
            if target_clean.lower() in card_clean.lower():
                similarity = max(similarity, 0.8)

            if similarity > best_score:
                best_score = similarity
                best_match = card

        return (best_match, best_score) if best_score >= threshold else (None, 0)

    def _clean_card_name(self, card_name: str) -> str:
        """Clean card name for comparison"""
        # Remove common suffixes/prefixes that might differ
        clean_name = re.sub(r'\s*\([^)]*\)', '', card_name)  # Remove parentheses content
        clean_name = re.sub(r'\s*-\s*.*$', '', clean_name)  # Remove dash and everything after
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()  # Normalize whitespace
        return clean_name

    def print_deck_estimation(self, estimation_results: Dict):
        """Print a readable summary of deck price estimation"""
        print(f"\n{'=' * 60}")
        print("DECK PRICE ESTIMATION")
        print(f"{'=' * 60}")
        print(f"Language preference: {estimation_results['language_preference']}")
        print(f"Fallback to foreign: {estimation_results['fallback_to_foreign']}")
        print(f"Optimize for minimum prices: {estimation_results['optimize_for_min_price']}")

        total = estimation_results['total_estimation']
        print(f"\n--- TOTAL ESTIMATION ---")
        print(f"Cards found: {total['cards_found']}/{total['total_cards_needed']}")
        print(f"Cards not found: {total['cards_not_found']}")
        print(f"Price range: €{total['min_price']:.2f} - €{total['max_price']:.2f}")
        print(f"Average estimate: €{total['mean_price']:.2f}")
        print(f"Median estimate: €{total['median_price']:.2f}")
        print(f"🎯 OPTIMIZED PRICE: €{total['optimized_price']:.2f}")

        print(f"\n--- BY CATEGORY ---")
        for category, category_data in estimation_results['categories'].items():
            totals = category_data['category_totals']
            print(f"{category}:")
            print(f"  Range: €{totals['min_price']:.2f} - €{totals['max_price']:.2f}")
            print(f"  Optimized: €{totals['optimized_price']:.2f}")

        print(f"\n--- PURCHASE STRATEGY ---")
        strategy_by_language = {}
        for item in estimation_results['purchase_strategy']:
            lang = item['language']
            if lang not in strategy_by_language:
                strategy_by_language[lang] = []
            strategy_by_language[lang].append(item)

        for language, items in strategy_by_language.items():
            print(f"\n{language.upper()} Cards:")
            lang_total = sum(item['total_price'] for item in items)
            print(f"  Subtotal: €{lang_total:.2f}")

            for item in items:
                feasible_icon = "✓" if item['feasible'] else "⚠️"
                similarity_icon = "🎯" if item['similarity'] > 0.9 else "📍" if item['similarity'] > 0.7 else "❓"
                print(
                    f"  {feasible_icon} {similarity_icon} {item['card']} x{item['quantity']} = €{item['total_price']:.2f}")
                print(f"      (€{item['unit_price']:.2f} each)")
                if item['matched_card'] != item['card']:
                    print(f"      → Matched: {item['matched_card']} (similarity: {item['similarity']:.2f})")

        if estimation_results['not_found_cards']:
            print(f"\n--- CARDS NOT FOUND ---")
            for card in estimation_results['not_found_cards']:
                print(f"❌ {card['category']}: {card['card_name']} - {card['reason']}")

    def save_estimation_to_file(self, estimation_results: Dict, output_path: str):
        """Save estimation results to a text file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("DECK PRICE ESTIMATION REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Language preference: {estimation_results['language_preference']}\n")
            f.write(f"Optimized price: €{estimation_results['total_estimation']['optimized_price']:.2f}\n\n")

            # Write purchase strategy
            f.write("PURCHASE STRATEGY:\n")
            f.write("-" * 30 + "\n")
            for item in estimation_results['purchase_strategy']:
                f.write(f"{item['card']} x{item['quantity']} - €{item['total_price']:.2f} ({item['language']})\n")
                if item['matched_card'] != item['card']:
                    f.write(f"  → Matched: {item['matched_card']}\n")

            f.write(f"\nTOTAL: €{estimation_results['total_estimation']['optimized_price']:.2f}\n")


def main():
    """Main function to estimate deck prices"""
    print("🃏 DECK PRICE ESTIMATOR")
    print("=" * 40)

    # Get today's date for analysis
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Using analysis data from: {today}")

    # Initialize estimator
    estimator = DeckPriceEstimator("./output", "./decks")

    # Interactive deck selection
    selected_deck_path = estimator.select_deck_interactive()
    if not selected_deck_path:
        print("❌ No deck selected. Exiting.")
        return

    # Load deck from YAML
    deck_list = estimator.load_deck_from_yaml(selected_deck_path)
    if not deck_list:
        print("❌ Failed to load deck list. Exiting.")
        return

    # Get the cards section from YAML
    cards = deck_list.get('cards', {})
    deck_name = deck_list.get('deck_name', 'Unknown Deck')

    print(f"\n📋 Analyzing deck: {deck_name}")
    total_cards = sum(sum(category.values()) for category in cards.values())
    print(f"Total cards needed: {total_cards}")

    # Load analysis data
    print(f"\n📊 Loading price analysis data...")
    analysis_data = estimator.analyzer.analyze_date_folder(today)

    if 'error' in analysis_data:
        print(f"❌ Error loading analysis data: {analysis_data['error']}")
        return

    print(f"✓ Loaded data from {analysis_data['total_excel_files']} Excel files")

    # Run estimations for both English and Foreign preferences
    print(f"\n💰 ESTIMATING PRICES...")

    # English preference
    print(f"\n--- English Preference ---")
    english_estimation = estimator.estimate_deck_price(
        cards, analysis_data,
        language_preference='English',
        fallback_to_foreign=True,
        optimize_for_min_price=True
    )
    estimator.print_deck_estimation(english_estimation)

    # Foreign preference
    print(f"\n--- Foreign Preference ---")
    foreign_estimation = estimator.estimate_deck_price(
        cards, analysis_data,
        language_preference='Foreign',
        fallback_to_foreign=True,  # Enable fallback for better matching
        optimize_for_min_price=True
    )
    estimator.print_deck_estimation(foreign_estimation)

    # Save results
    output_dir = Path("./deck_estimates")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    english_file = output_dir / f"{deck_name.replace(' ', '_')}_english_{timestamp}.txt"
    foreign_file = output_dir / f"{deck_name.replace(' ', '_')}_foreign_{timestamp}.txt"

    estimator.save_estimation_to_file(english_estimation, english_file)
    estimator.save_estimation_to_file(foreign_estimation, foreign_file)

    print(f"\n💾 RESULTS SAVED:")
    print(f"English estimates: {english_file}")
    print(f"Foreign estimates: {foreign_file}")

    # Summary comparison
    print(f"\n📊 SUMMARY COMPARISON:")
    print(f"English optimized price: €{english_estimation['total_estimation']['optimized_price']:.2f}")
    print(f"Foreign optimized price:  €{foreign_estimation['total_estimation']['optimized_price']:.2f}")

    savings = english_estimation['total_estimation']['optimized_price'] - foreign_estimation['total_estimation'][
        'optimized_price']
    if savings > 0:
        print(f"💡 Potential savings with foreign cards: €{savings:.2f}")
    else:
        print(f"💡 English cards are cheaper by: €{abs(savings):.2f}")


if __name__ == "__main__":
    main()