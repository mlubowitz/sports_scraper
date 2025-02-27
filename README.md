# Sports Betting Data Scraper

A web application that scrapes player statistics and odds from sports betting websites. This tool allows users to select leagues and statistics of interest, then view and download the resulting data.

## Features

- **League Selection:** Choose one or more sports leagues to scrape data from
- **Statistic Selection:** Select which player statistic to analyze (passes, shots, tackles, etc.)
- **Web Interface:** Easy-to-use UI for configuring and running scraping jobs
- **API Backend:** Robust API built with Flask for handling scraping requests
- **Concurrent Processing:** Efficiently scrape multiple leagues simultaneously
- **Data Visualization:** View scraped data in a tabular format
- **CSV Export:** Download results as CSV files for further analysis

## Project Structure

```
sports_scraper/
├── api/               # Flask API
│   └── app.py
├── data/              # Output directory for CSV files
├── frontend/          # Frontend static files
│   ├── css/
│   ├── js/
│   └── index.html
├── logs/              # Log files
├── scraper/           # Core scraping functionality
│   ├── config.py
│   └── scraper.py
├── static/            # Static assets for web UI
│   ├── css/
│   └── js/
├── templates/         # HTML templates
├── venv/              # Virtual environment
├── requirements.txt   # Python dependencies
└── run.py             # Main entry point
```

## Installation

### Prerequisites

- Python 3.8+
- Google Chrome browser (for Selenium)
- MacOS with Homebrew installed

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sports_scraper.git
   cd sports_scraper
   ```

2. Run the setup script to create the virtual environment and install dependencies:
   ```bash
   # Make the setup script executable
   chmod +x setup.sh
   # Run the setup script
   ./setup.sh
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Usage

### Running the Web Interface

1. Start the Flask API server:
   ```bash
   python run.py api
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Use the web interface to:
   - Select leagues from the checkboxes
   - Choose a statistic using the radio buttons
   - Click "Start Scraping" to begin the data collection process
   - View job status and results
   - Download CSV files with the collected data

### Running the Scraper Directly

You can also run the scraper from the command line without using the web interface:

```bash
python run.py scrape --leagues EPL "La Liga" --statistic Passes
```

## Configuration

The scraper settings can be modified in the `scraper/config.py` file:

- `AVAILABLE_LEAGUES`: List of leagues that can be scraped
- `AVAILABLE_STATISTICS`: List of statistics that can be collected
- `DEFAULT_MAX_WORKERS`: Maximum number of concurrent browser instances
- `OUTPUT_DIR`: Directory for storing output CSV files

## Extending the Scraper

To add support for new leagues or statistics:

1. Update the `AVAILABLE_LEAGUES` or `AVAILABLE_STATISTICS` lists in `config.py`
2. Test that the website has appropriate selectors for the new items
3. If needed, modify the `process_league()` method in `scraper.py` to handle any site-specific differences

## Troubleshooting

### CAPTCHA Issues

If you encounter CAPTCHA challenges:

1. Reduce the scraping frequency by increasing the delay between requests
2. Try using a different IP address or VPN
3. Implement a CAPTCHA solving service integration

### Browser Driver Issues

If you have problems with the Chrome driver:

1. Update the Chrome browser to the latest version
2. Verify that the webdriver-manager package is working correctly
3. Try manually downloading the ChromeDriver appropriate for your Chrome version

## License

This project is licensed under the MIT License - see the LICENSE file for details.