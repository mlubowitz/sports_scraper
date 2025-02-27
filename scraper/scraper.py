import os
import time
import csv
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

# Lock for synchronizing CSV writes
csv_lock = threading.Lock()

class SportsScraper:
    def __init__(self, output_dir=None):
        """Initialize the scraper with configurable output directory"""
        self.output_dir = output_dir or os.getcwd()
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def check_for_captcha(self, driver):
        """Check if a CAPTCHA is present on the page"""
        captcha_indicators = [
            "//iframe[contains(@src, 'captcha')]",
            "//iframe[contains(@src, 'recaptcha')]",
            "//div[contains(@class, 'captcha')]",
            "//div[contains(@class, 'g-recaptcha')]"
        ]
        
        for indicator in captcha_indicators:
            if len(driver.find_elements(By.XPATH, indicator)) > 0:
                return True
        return False

    def create_driver(self):
        """Create and configure a Chrome WebDriver instance with anti-detection measures"""
        chrome_options = Options()
        
        # Enhanced stealth settings
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Additional stealth arguments
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Performance optimization flags
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-translate')
        chrome_options.add_argument('--disable-extensions')
        
        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Enhanced stealth scripts
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Additional stealth JavaScript
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            window.navigator.chrome = {
                runtime: {}
            };
        """)
        
        return driver

    def write_to_csv(self, data, filename):
        """Thread-safe CSV writer that appends rows to the given file"""
        with csv_lock:
            file_exists = os.path.isfile(filename)
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ["game", "player", "team", "statistic", "value", "odds"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(data)

    def get_output_filename(self, leagues, statistic):
        """Generate a filename based on the leagues and statistic"""
        league_str = "_".join(leagues)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"{league_str}_{statistic}_{timestamp}.csv")

    def process_league(self, league_name, statistic, output_file):
        """Process a single league and statistic combination"""
        driver = None
        try:
            driver = self.create_driver()
            wait = WebDriverWait(driver, 15)
            
            print(f"Accessing website for {league_name}, statistic: {statistic}...")
            driver.get("https://troya.xyz/betbuilder?sb=betus")
            time.sleep(5)  # Initial load wait
            
            if self.check_for_captcha(driver):
                raise Exception("CAPTCHA detected - aborting scrape")
                
            print(f"Looking for league: {league_name}")
            
            # Find and click league
            league_element = wait.until(EC.presence_of_element_located((
                By.XPATH,
                f"//div[contains(@class, 'ligues-slider__item')]//div[contains(@class, 'ligues-slider__ligue-name') and contains(text(), '{league_name}')]"
            )))
            print(f"Found {league_name} element")
            
            league_parent = league_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ligues-slider__item')]")
            driver.execute_script("arguments[0].click();", league_parent)
            print(f"Clicked {league_name}")
            
            time.sleep(2)
            
            if self.check_for_captcha(driver):
                raise Exception("CAPTCHA detected after league selection - aborting scrape")
            
            # Find and click statistic button
            stat_button = wait.until(EC.element_to_be_clickable((
                By.XPATH,
                f"//div[contains(@class, 'main-markets__item')]//p[contains(text(), '{statistic}')]/.."
            )))
            driver.execute_script("arguments[0].click();", stat_button)
            print(f"Clicked {statistic} button for {league_name}")
            
            time.sleep(2)
            
            if self.check_for_captcha(driver):
                raise Exception(f"CAPTCHA detected after selecting {statistic} - aborting scrape")
            
            # Find all game headers
            game_headers = wait.until(EC.presence_of_all_elements_located((
                By.XPATH,
                "//div[contains(@class, 'tiered-block__item__top')]"
            )))
            print(f"Found {len(game_headers)} games for {league_name}")
            
            # Process each game
            for header in game_headers:
                game_data = []  # Store data for current game
                try:
                    # Click to expand the game
                    driver.execute_script("arguments[0].click();", header)
                    time.sleep(1)
                    
                    # Find the associated container (parent element)
                    container = header.find_element(By.XPATH, "./..")
                    
                    team_spans = container.find_elements(
                        By.XPATH,
                        ".//p[contains(@class, 'tiered-block__player-team')]//span"
                    )
                    
                    if len(team_spans) < 2:
                        continue
                        
                    game_title = f"{team_spans[0].text} vs {team_spans[1].text}"
                    print(f"Processing game: {game_title}")
                    
                    player_containers = container.find_elements(
                        By.CSS_SELECTOR,
                        "div.shots-block__player"
                    )
                    
                    for player_container in player_containers:
                        try:
                            player_name = player_container.find_element(
                                By.XPATH,
                                ".//p[contains(@class, 'shots-block') and contains(@class, 'player-name')]"
                            ).text.strip()
                            
                            team_name = player_container.find_element(
                                By.XPATH,
                                ".//p[contains(@class, 'shots-block') and contains(@class, 'player-team')]"
                            ).text.strip()
                            
                            market_items = player_container.find_elements(
                                By.XPATH,
                                ".//div[contains(@class, 'markets-slider') and contains(@class, 'item')]"
                            )
                            
                            for item in market_items:
                                value = item.find_element(
                                    By.XPATH,
                                    ".//p[contains(@class, 'markets-slider') and contains(@class, 'amount')]"
                                ).text.strip()
                                
                                odds = item.find_element(
                                    By.XPATH,
                                    ".//p[contains(@class, 'markets-slider') and contains(@class, 'stat')]"
                                ).text.strip()
                                
                                game_data.append({
                                    "game": game_title,
                                    "player": player_name,
                                    "team": team_name,
                                    "statistic": statistic,
                                    "value": value,
                                    "odds": odds
                                })
                                
                        except Exception as e:
                            print(f"Error processing player in {game_title}: {e}")
                            continue
                    
                    # Write game data to CSV after processing the entire game
                    if game_data:
                        self.write_to_csv(game_data, output_file)
                        print(f"Wrote {len(game_data)} records for game: {game_title}")
                        
                except Exception as e:
                    print(f"Error processing game in {league_name}: {e}")
                    continue
                
        except Exception as e:
            print(f"Major error processing league {league_name}: {e}")
        
        finally:
            if driver:
                driver.quit()

    def scrape_data(self, leagues, statistic, max_workers=3):
        """
        Scrape data for the specified leagues and statistic
        
        Args:
            leagues (list): List of league names to scrape
            statistic (str): Statistic to scrape (e.g., "Passes", "Shots")
            max_workers (int): Maximum number of concurrent browser instances
            
        Returns:
            str: Path to the output CSV file
        """
        import concurrent.futures
        
        # Generate output filename
        output_file = self.get_output_filename(leagues, statistic)
        
        # Actually use the smaller of max_workers or number of leagues
        num_workers = min(max_workers, len(leagues))
        
        print(f"Starting scraper with {num_workers} concurrent browsers")
        print(f"Output file: {output_file}")
        
        # Process leagues with delays between starts
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {}
            
            # Submit leagues in batches respecting max_workers limit
            for i, league in enumerate(leagues):
                # Submit the league processing task
                future = executor.submit(self.process_league, league, statistic, output_file)
                futures[future] = league
                print(f"Started processing {league}")
                
                # Add delay before starting next thread (except for last league)
                if i < len(leagues) - 1:
                    delay = 5  # 5 second delay between thread starts
                    print(f"Waiting {delay} seconds before starting next browser...")
                    time.sleep(delay)
                
            # Wait for all tasks to complete and show progress
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                league = futures[future]
                try:
                    future.result()
                    completed += 1
                    print(f"Completed processing {league} ({completed}/{len(leagues)} leagues done)")
                except Exception as e:
                    print(f"League {league} generated an exception: {e}")
        
        return output_file