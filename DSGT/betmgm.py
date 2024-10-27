import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Selenium
options = Options()
options.headless = False  # Set to False to see the browser window
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL of the page
url = "https://sports.nj.betmgm.com/en/sports/soccer-4"
driver.get(url)

# Wait for content to load
time.sleep(5)  # Adjust as necessary

# Lists to store data
games = []
home_win_odds = []
draw_odds = []
away_win_odds = []
home_win_prob = []
draw_prob = []
away_win_prob = []

# Function to convert American odds to decimal odds
def american_to_decimal(odd):
    if odd > 0:
        return (odd / 100) + 1
    else:
        return (100 / abs(odd)) + 1

# Locate each game row
game_rows = driver.find_elements(By.CSS_SELECTOR, 'ms-event.grid-event')
print(f"Found {len(game_rows)} game rows")  # Debugging statement

for row in game_rows:
    try:
        # Extract team names
        teams = row.find_elements(By.CSS_SELECTOR, 'div.participant-info .participant')
        if len(teams) >= 2:
            game_name = f"{teams[0].text} vs {teams[1].text}"
            games.append(game_name)
            print(f"Game: {game_name}")  # Debugging

        # Extract odds
        odds = row.find_elements(By.CSS_SELECTOR, 'span.custom-odds-value-style')
        print(f"Odds found: {[odd.text for odd in odds]}")  # Debugging
        if len(odds) >= 3:
            # Convert American odds to decimal and calculate implied probabilities
            home_odds = american_to_decimal(float(odds[0].text.replace('+', '')))
            draw_odds_value = american_to_decimal(float(odds[1].text.replace('+', '')))
            away_odds = american_to_decimal(float(odds[2].text.replace('+', '')))
            
            home_win_odds.append(home_odds)
            draw_odds.append(draw_odds_value)
            away_win_odds.append(away_odds)
            
            # Calculate implied probabilities
            home_win_prob.append(round((1 / home_odds) * 100, 2))
            draw_prob.append(round((1 / draw_odds_value) * 100, 2))
            away_win_prob.append(round((1 / away_odds) * 100, 2))
        else:
            # If odds are missing, add None values
            home_win_odds.append(None)
            draw_odds.append(None)
            away_win_odds.append(None)
            home_win_prob.append(None)
            draw_prob.append(None)
            away_win_prob.append(None)
    except Exception as e:
        print(f"Error extracting data for a row: {e}")
        continue

# Close the browser
driver.quit()

# Create a DataFrame
df = pd.DataFrame({
    'Game': games,
    'Home Win Odds (1)': home_win_odds,
    'Draw Odds (X)': draw_odds,
    'Away Win Odds (2)': away_win_odds,
    'Home Win Probability (%)': home_win_prob,
    'Draw Probability (%)': draw_prob,
    'Away Win Probability (%)': away_win_prob
})

# Print DataFrame content for debugging
print(df)

# Save the DataFrame as a CSV file
df.to_csv('betmgm_odds_with_probabilities.csv', index=False)
print("Data saved to 'betmgm_odds_with_probabilities.csv'")