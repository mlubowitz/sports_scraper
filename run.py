#!/usr/bin/env python
"""
Main entry point for the Sports Betting Scraper application.
"""
import os
import sys
import argparse

def setup_environment():
    """Create required directories if they don't exist"""
    directories = ['data', 'logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

def run_api():
    """Run the Flask API server"""
    from api.app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

def run_scraper(leagues, statistic):
    """Run the scraper directly without the API"""
    from scraper.scraper import SportsScraper
    from scraper.config import AVAILABLE_LEAGUES, AVAILABLE_STATISTICS
    
    # Validate inputs
    invalid_leagues = [league for league in leagues if league not in AVAILABLE_LEAGUES]
    if invalid_leagues:
        print(f"Error: Invalid leagues: {', '.join(invalid_leagues)}")
        print(f"Available leagues: {', '.join(AVAILABLE_LEAGUES)}")
        return
    
    if statistic not in AVAILABLE_STATISTICS:
        print(f"Error: Invalid statistic: {statistic}")
        print(f"Available statistics: {', '.join(AVAILABLE_STATISTICS)}")
        return
    
    # Create and run the scraper
    scraper = SportsScraper(output_dir='data')
    output_file = scraper.scrape_data(leagues, statistic)
    
    print(f"Scraping completed. Output file: {output_file}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Sports Betting Scraper')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # API subcommand
    api_parser = subparsers.add_parser('api', help='Run the API server')
    
    # Scraper subcommand
    scraper_parser = subparsers.add_parser('scrape', help='Run the scraper directly')
    scraper_parser.add_argument('--leagues', '-l', nargs='+', required=True, 
                               help='Leagues to scrape (e.g., EPL "La Liga")')
    scraper_parser.add_argument('--statistic', '-s', required=True,
                               help='Statistic to scrape (e.g., Passes, Shots)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set up the environment
    setup_environment()
    
    # Run the appropriate command
    if args.command == 'api':
        run_api()
    elif args.command == 'scrape':
        run_scraper(args.leagues, args.statistic)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()