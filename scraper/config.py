"""
Configuration settings for the sports scraper
"""

# List of available leagues to scrape
AVAILABLE_LEAGUES = [
    "EPL",
    "La Liga", 
    "Serie A", 
    "Bundesliga", 
    "Ligue 1",
    "MLS",
    "Championship"
]

# List of available statistics to scrape
AVAILABLE_STATISTICS = [
    "Passes",
    "Shots",
    "Tackles",
    "Interceptions", 
    "Blocks",
    "Clearances",
    "Goals",
    "Assists"
]

# Default settings
DEFAULT_LEAGUE = "EPL"
DEFAULT_STATISTIC = "Passes"
DEFAULT_MAX_WORKERS = 3

# Base URL for the scraper
BASE_URL = "https://troya.xyz/betbuilder?sb=betus"

# Output directory for CSV files
OUTPUT_DIR = "data"