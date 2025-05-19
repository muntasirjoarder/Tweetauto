import os
import json
import random
import time
import requests
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
PROFILE_PATH = "Tweetify"  # Edge profile name
ACCOUNTS = [
    "https://x.com/Timesofgaza"
]
MAX_TWEETS_PER_ACCOUNT = 10


STANDARD_DELAYS = (0.8, 2.5)      # Basic actions - Twitter users move quickly
READING_DELAYS = (1.5, 8)        # Reading content - varies by tweet complexity & media
DECISION_DELAYS = (1.5, 4)        # Making decisions - Twitter is designed for quick engagement
MICRO_DELAYS = (0.1, 0.5)         # Small movements - human reaction time minimums
DISTRACTION_PROBABILITY = 0.08    # Occasional longer pause - Twitter sessions are typically focused

def close_edge_processes():
    """Close all running Edge processes"""
    print("Attempting to close all Edge processes...")
    closed = 0
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'msedge.exe' in proc.info['name'].lower():
            try:
                proc.terminate()
                closed += 1
            except:
                pass
    if closed > 0:
        print(f"Closed {closed} Edge processes")
        time.sleep(2)  # Give time for processes to end
    return closed

def get_exact_edge_profile_path(profile_name="Tweetify"):
    """Find the exact Edge profile path"""
    base_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data')
    
    for profile_dir in ['Default'] + [f'Profile {i}' for i in range(1, 10)]:
        profile_path = os.path.join(base_path, profile_dir)
        prefs_file = os.path.join(profile_path, 'Preferences')
        
        if os.path.exists(prefs_file):
            try:
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    if prefs.get('profile', {}).get('name') == profile_name:
                        return profile_path
            except:
                continue
    
    profile_path = os.path.join(base_path, profile_name)
    if os.path.exists(profile_path):
        return profile_path
    
    available = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    raise FileNotFoundError(f"Profile '{profile_name}' not found. Available profiles: {available}")

def human_delay(delay_type="standard"):
    """
    Sophisticated human-like delay with variable timing
    
    Parameters:
        delay_type: Type of delay to simulate
            - "standard": Regular actions (1.5-3.5s)
            - "reading": Reading content (4-9s) 
            - "decision": Making decisions (2.5-5s)
            - "micro": Small adjustments (0.2-0.8s)
    """
    # Occasionally simulate a distraction (checking phone, etc.)
    if random.random() < DISTRACTION_PROBABILITY:
        time.sleep(random.uniform(7, 15))
        return
    
    if delay_type == "reading":
        time.sleep(random.uniform(*READING_DELAYS))
    elif delay_type == "decision":
        time.sleep(random.uniform(*DECISION_DELAYS))
    elif delay_type == "micro":
        time.sleep(random.uniform(*MICRO_DELAYS))
    else:  # standard
        time.sleep(random.uniform(*STANDARD_DELAYS))

def scroll_randomly(driver):
    """Scroll randomly to mimic human behavior"""
    # First pause briefly to look at current content
    human_delay("reading")
    
    for _ in range(random.randint(2, 4)):
        # Random scroll distance for each movement
        scroll_distance = random.randint(300, 700)
        
        # Sometimes do smooth scroll in chunks
        if random.random() > 0.6:
            chunks = random.randint(3, 5)
            for chunk in range(chunks):
                driver.execute_script(f"window.scrollBy(0, {scroll_distance//chunks})")
                human_delay("micro")
        else:
            # Single scroll movement
            driver.execute_script(f"window.scrollBy(0, {scroll_distance})")
        
        # Pause to read new content that appeared
        human_delay("reading")
    
    # Occasionally scroll back up slightly
    if random.random() > 0.7:
        driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)})")
        human_delay("standard")

def read_comments(driver):
    """Mimic reading comments on a tweet"""
    # First read the main tweet
    human_delay("reading")
    
    # Scroll down slowly to read comments (shorter scrolls than regular scrolling)
    num_scrolls = random.randint(2, 5)  # Read 2-5 comment sections
    
    for i in range(num_scrolls):
        # Shorter scroll distances for comment sections
        scroll_distance = random.randint(200, 400)
        
        # Smooth scrolling to mimic reading carefully
        if random.random() > 0.3:  # 70% chance of smooth scrolling for comments
            chunks = random.randint(4, 7)  # More chunks for smoother scrolling
            for chunk in range(chunks):
                driver.execute_script(f"window.scrollBy(0, {scroll_distance//chunks})")
                human_delay("micro")
        else:
            driver.execute_script(f"window.scrollBy(0, {scroll_distance})")
        
        # Spend time reading the comments
        read_time = random.uniform(3, 8)  # Slightly shorter than main content reading
        time.sleep(read_time)
        
        # Occasionally scroll back up slightly to re-read something interesting
        if random.random() > 0.7:
            driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 150)})")
            human_delay("reading")
            # And then continue down
            driver.execute_script(f"window.scrollBy(0, {random.randint(70, 170)})")
    
    # After reading comments, scroll back up toward the tweet before retweeting
    driver.execute_script(f"window.scrollBy(0, -{random.randint(300, 600)})")
    human_delay("standard")

def setup_driver():
    """Configure Edge browser with specified profile"""
    edge_options = Options()
    
    # Find the exact profile path using the function
    profile_path = get_exact_edge_profile_path(PROFILE_PATH)
    print(f"Found profile path: {profile_path}")
    
    # Set the user data directory to the parent directory of the profile
    edge_options.add_argument(f"user-data-dir={os.path.dirname(profile_path)}")
    
    # Set the profile directory to the actual profile folder name
    edge_options.add_argument(f"profile-directory={os.path.basename(profile_path)}")
    
    # Anti-detection settings
    edge_options.add_argument("--disable-blink-features=AutomationControlled")
    edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    edge_options.add_experimental_option("useAutomationExtension", False)
    
    try:
        service = Service(executable_path="msedgedriver.exe")
        driver = webdriver.Edge(service=service, options=edge_options)
        driver.maximize_window()
        print(f"Successfully opened Edge with profile: {PROFILE_PATH}")
        print(f"Current URL: {driver.current_url}")  # Debug info
        return driver
    except Exception as e:
        print(f"Error opening Edge browser: {str(e)}")
        raise

def scrape_tweet_urls(driver, account_url):
    """Scrape latest tweet URLs from an account, excluding pinned tweet"""
    print(f"Visiting {account_url}")
    driver.get(account_url)
    human_delay("reading")  # Reading the timeline
    
    # Wait for tweets to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
    )
    
    # Scroll a bit to load more tweets
    scroll_randomly(driver)
    
    # Get all tweet links
    tweet_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet'] a[href*='/status/']")
    
    # Extract unique tweet URLs
    tweet_urls = set()
    for elem in tweet_elements:
        href = elem.get_attribute("href")
        if "/status/" in href and not any(s in href for s in ["/photo/", "/video/", "/analytics"]):
            tweet_urls.add(href.split('?')[0])  # Remove query params
    
    # Convert to list and exclude the first tweet (often pinned)
    tweet_urls = list(tweet_urls)[1:MAX_TWEETS_PER_ACCOUNT+1]
    
    print(f"Found {len(tweet_urls)} tweets from {account_url}")
    return tweet_urls

def retweet_if_needed(driver, tweet_url):
    """Retweet a tweet if not already retweeted. Returns True if newly retweeted, False otherwise."""
    print(f"Checking {tweet_url}")
    driver.get(tweet_url)
    human_delay("reading")  # Initial reading of the tweet content
    
    try:
        # Wait for tweet to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
        )
        
        # Read through comments before deciding to retweet (mimics human behavior)
        read_comments(driver)
        
        # After reading, locate the retweet button
        retweet_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='retweet']"))
        )
        
        # Check if already retweeted (button text changes)
        if "Undo retweet" not in retweet_button.get_attribute("innerHTML"):
            # Decision time before retweeting (after reading comments)
            human_delay("decision")
            retweet_button.click()
            
            # Click confirm in the popup
            confirm_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='retweetConfirm']"))
            )
            human_delay("micro")  # Quick decision for confirmation
            confirm_button.click()
            print("Retweeted successfully")
            
            # Sometimes like the tweet after retweeting (human behavior)
            if random.random() > 0.7:  # 30% chance to like after retweeting
                try:
                    like_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='like']")
                    human_delay("standard")
                    like_button.click()
                    print("Also liked the tweet")
                except:
                    pass
                
            human_delay("standard")  # Pause after completion
            return True  # Successfully retweeted
        else:
            print("Already retweeted")
            human_delay("micro")  # Quick reaction when seeing already retweeted
            return False  # Was already retweeted
    except Exception as e:
        print(f"Could not retweet: {str(e)}")
        return False  # Failed to retweet

def main():
    driver = setup_driver()
    retweet_count = 0  # Initialize counter for successful retweets
    
    try:
        # Shuffle accounts for random order
        random.shuffle(ACCOUNTS)
        
        # Scrape tweets from each account
        all_tweet_urls = []
        for account in ACCOUNTS:
            try:
                tweet_urls = scrape_tweet_urls(driver, account)
                all_tweet_urls.extend(tweet_urls)
                human_delay("decision")  # Deciding which account to check next
            except Exception as e:
                print(f"Error scraping {account}: {str(e)}")
                continue
        
        # Shuffle all collected tweets
        random.shuffle(all_tweet_urls)
        print(f"\nTotal tweets to process: {len(all_tweet_urls)}")
        
        # Process each tweet
        for i, tweet_url in enumerate(all_tweet_urls, 1):
            print(f"\nProcessing tweet {i}/{len(all_tweet_urls)}")
            try:
                if retweet_if_needed(driver, tweet_url):
                    retweet_count += 1  # Increment counter for successful retweets
            except Exception as e:
                print(f"Error processing tweet: {str(e)}")
                continue
    
    finally:
        print(f"\nSuccessfully retweeted {retweet_count} tweets")
        print("\nClosing browser in 5 seconds...")
        time.sleep(5)
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    close_edge_processes()
    main()