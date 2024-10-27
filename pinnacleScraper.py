import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in the background
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Automatically download and set up ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the Pinnacle Premier League page
url = "https://www.pinnacle.com/en/soccer/england-premier-league/matchups/#all"
driver.get(url)

# Allow time for the page to load
time.sleep(5)

# Data storage for matches and odds
match_data = []

# Example of scraping odds for a specific match
try:
    # Locate the specific odds for Liverpool to win using XPath or other selector
    home_odds_element = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/main/div/div[4]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[1]/button/span")  # Update this XPath with the actual value you found
    home_win_odds = float(home_odds_element.text)

    draw_odds_element = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/main/div/div[4]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[2]/button/span")  # Update this XPath with the actual value you found
    draw_odds = float(draw_odds_element.text)

    away_odds_element = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/main/div/div[4]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div[3]/button/span")  # Update this XPath with the actual value you found
    away_win_odds = float(away_odds_element.text)

    # Example data storage for this match
    match_data.append(['Home vs. Away', home_win_odds, draw_odds, away_win_odds])  # Draw and away odds can be filled similarly

    print(f"Home Win Odds: {home_win_odds}")  # Debugging output
    print(f"Draw Odds: {draw_odds}")  # Debugging output
    print(f"Away Win Odds: {away_win_odds}")  # Debugging output

except Exception as e:
    print(f"Error retrieving odds: {e}")

# Close the WebDriver
driver.quit()