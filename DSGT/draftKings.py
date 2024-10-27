import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Selenium
options = Options()
options.headless = False
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL of the DraftKings page with odds
url = "https://sportsbook.draftkings.com/leagues/soccer/england---premier-league"  # replace with the correct DraftKings URL
driver.get(url)

# Wait for the game rows to load
time.sleep(5)

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
game_rows = driver.find_elements(By.CSS_SELECTOR, '.sportsbook-event-accordion__wrapper')
print(f"Found {len(game_rows)} game rows")

for row in game_rows:
    try:
        # Extract team names
        teams = row.find_elements(By.CSS_SELECTOR, 'a.sportsbook-event-accordion__title')
        if len(teams) == 1:
            game_name = teams[0].text
            games.append(game_name)
            print(f"Game: {game_name}")

        # Extract odds
        odds_elements = row.find_elements(By.CSS_SELECTOR, 'span.sportsbook-odds')
        if len(odds_elements) >= 3:
            # Clean the odds text and handle non-standard negative sign
            home_odd_text = odds_elements[0].text.replace('−', '-')
            draw_odd_text = odds_elements[1].text.replace('−', '-')
            away_odd_text = odds_elements[2].text.replace('−', '-')
            
            # Convert American odds to decimal
            home_odds = american_to_decimal(float(home_odd_text))
            draw_odds_value = american_to_decimal(float(draw_odd_text))
            away_odds = american_to_decimal(float(away_odd_text))

            # Append odds
            home_win_odds.append(home_odds)
            draw_odds.append(draw_odds_value)
            away_win_odds.append(away_odds)

            # Calculate implied probabilities
            implied_home_prob = (1 / home_odds) * 100
            implied_draw_prob = (1 / draw_odds_value) * 100
            implied_away_prob = (1 / away_odds) * 100

            # Normalize probabilities to sum to 100%
            total_prob = implied_home_prob + implied_draw_prob + implied_away_prob
            home_win_prob.append(round((implied_home_prob / total_prob) * 100, 2))
            draw_prob.append(round((implied_draw_prob / total_prob) * 100, 2))
            away_win_prob.append(round((implied_away_prob / total_prob) * 100, 2))
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
        # Add None values to ensure equal list lengths
        games.append(game_name)
        home_win_odds.append(None)
        draw_odds.append(None)
        away_win_odds.append(None)
        home_win_prob.append(None)
        draw_prob.append(None)
        away_win_prob.append(None)
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
df.to_csv('draftkings_odds_with_probabilities.csv', index=False)
print("Data saved to 'draftkings_odds_with_probabilities.csv'")