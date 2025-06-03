# CardMarket Scraper

A professional, sequential web scraper for CardMarket YuGiOh card listings. This tool extracts card pricing and seller information and exports it to Excel files.

## Features

- **Sequential Processing**: Reliable, one-card-at-a-time scraping to avoid detection
- **Professional Structure**: Clean, modular code with single responsibility principles
- **Excel Export**: Automatic Excel file generation with clickable URLs and proper formatting
- **Configuration-Based**: Easy YAML configuration for different card lists
- **Error Handling**: Comprehensive error handling and progress tracking
- **User-Friendly**: Simple command-line interface suitable for beginners

## Project Structure

```
cardmarket-scraper/
├── main.py                 # Main entry point
├── card_scraper.py         # Main scraper coordinator
├── config_manager.py       # Configuration file handling
├── url_builder.py          # URL construction logic
├── web_driver_manager.py   # Browser automation management
├── data_parser.py          # HTML parsing and data extraction
├── excel_exporter.py       # Excel file creation and formatting
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── config.yaml            # Example configuration file
```

## Installation

1. **Install Python** (3.8 or higher)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome** and make sure it's in your system PATH

4. **Download ChromeDriver** matching your Chrome version and place it in your PATH

## Setup

1. **Start Chrome with remote debugging**:
   ```bash
   chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/chrome-debug"
   
   OR
   
   chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/chrome-dev"
   
   OR
   
   C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/chrome-dev"
   ```

2. **Create a config.yaml file** (see example below)

3. **Run the scraper**:
   ```bash
   python main.py
   ```

## Configuration File Example

Create a `config.yaml` file with your card list:

```yaml
name: "My Card List"
wait_time: 3

cards:
  "Blue-Eyes-White-Dragon":
    set: "LOB-Legend-of-Blue-Eyes-White-Dragon"
    condition: "Near Mint"
    edition: "1st"
  
  "Dark-Magician":
    set: "LOB-Legend-of-Blue-Eyes-White-Dragon"
    condition: "Near Mint"
  
  "Red-Eyes-Black-Dragon":
    set: "LOB-Legend-of-Blue-Eyes-White-Dragon"
```

### Configuration Options

- **name**: Name for your card list (used in Excel filename)
- **wait_time**: Seconds to wait between page loads (default: 3)
- **cards**: Dictionary of card names and their settings
  - **set**: CardMarket set identifier (optional)
  - **condition**: Filter by condition ("Near Mint", etc.)
  - **edition**: Filter by edition ("1st" for first edition)

## Usage

### Basic Usage

```bash
python main.py
```

Follow the prompts to enter your config file name and start scraping.

### Manual Testing

For testing individual URLs:

```bash
python main.py --manual
```

## Output

The scraper creates an Excel file with:
- **Timestamp in filename**: `MyCardList_2024_12_15.xlsx`
- **Separate sheets** for each card
- **Clickable URLs** in cell A1 of each sheet
- **Formatted data** starting at row 4
- **Auto-sized columns** for readability

### Data Fields

Each listing includes:
- `seller_username`: Seller's username
- `seller_sales_count`: Number of seller's completed sales
- `condition`: Card condition
- `condition_badge`: Condition indicator
- `language`: Card language
- `edition`: Edition information (1st edition if applicable)
- `price`: Listed price
- `quantity`: Available quantity

## Error Handling

The scraper includes comprehensive error handling:
- Invalid configuration files
- Network connection issues
- Missing page elements
- Chrome driver problems

Errors are logged with clear messages to help with troubleshooting.

## Best Practices

1. **Use reasonable wait times** (3-5 seconds) to avoid overloading the server
2. **Keep card lists manageable** (under 50 cards per session)
3. **Run during off-peak hours** when possible
4. **Monitor your Chrome debugging session** for any issues

## Troubleshooting

### Common Issues

**Chrome driver not found**:
- Ensure ChromeDriver is installed and in your PATH
- Check that your ChromeDriver version matches your Chrome version

**Connection refused**:
- Make sure Chrome is running with `--remote-debugging-port=9222`
- Check that no other processes are using port 9222

**Empty results**:
- Verify your card names match CardMarket URLs exactly
- Check that the CardMarket page structure hasn't changed

**Configuration errors**:
- Validate your YAML syntax
- Ensure all required fields are present

### Getting Help

1. Check the console output for specific error messages
2. Verify your configuration file format
3. Test with a single card first using manual mode
4. Ensure Chrome debugging is set up correctly

## Contributing

This project is designed to be simple and maintainable. Each module has a single responsibility:

- **ConfigManager**: Handles YAML loading and validation
- **URLBuilder**: Constructs CardMarket URLs
- **WebDriverManager**: Manages Chrome browser automation
- **DataParser**: Extracts data from HTML
- **ExcelExporter**: Creates formatted Excel files
- **CardScraper**: Coordinates the entire process

## License

This tool is for educational and personal use only. Please respect CardMarket's terms of service and use responsibly.
