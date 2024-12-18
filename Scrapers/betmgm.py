import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

TEAM_NAME_MAPPING = {
    "Man United": "Manchester United",
    "Chelsea": "Chelsea",
    "Fulham": "Fulham",
    "Brentford": "Brentford",
    "West Ham": "West Ham United",
    "Everton FC": "Everton",
    "Wolves": "Wolverhampton Wanderers",
    "Southampton FC": "Southampton",
    "Crystal Palace": "Crystal Palace",
    "Bournemouth": "AFC Bournemouth",
    "Brighton": "Brighton & Hove Albion",
    "Man City": "Manchester City",
    "Liverpool": "Liverpool",
    "Aston Villa": "Aston Villa",
    "Tottenham": "Tottenham Hotspur",
    "Ipswich Town": "Ipswich Town",
    "Leicester": "Leicester City",
    "Nottingham Forest": "Nottingham Forest",
    "Newcastle": "Newcastle United",
    "Arsenal": "Arsenal"
}

# Setup Selenium
options = Options()
driver = webdriver.Chrome(options=options)

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

# Function to calculate implied probability from American odds
def implied_probability(odd):
    if odd > 0:
        return 100 / (odd + 100)
    else:
        return abs(odd) / (abs(odd) + 100)

# Locate each game row
game_rows = driver.find_elements(By.CSS_SELECTOR, 'ms-event.grid-event')
print(f"Found {len(game_rows)} game rows")  # Debugging statement

# Limit the data collection to the first 10 rows
for i, row in enumerate(game_rows):
    try:
        # Extract team names
        teams = row.find_elements(By.CSS_SELECTOR, 'div.participant-info .participant')
        if len(teams) >= 2:
            # Map team names using the dictionary
            home_team = TEAM_NAME_MAPPING.get(teams[0].text, teams[0].text)
            away_team = TEAM_NAME_MAPPING.get(teams[1].text, teams[1].text)
            games.append(f"{home_team} vs {away_team}")

        # Extract odds
        odds = row.find_elements(By.CSS_SELECTOR, 'span.custom-odds-value-style')
        if len(odds) >= 3:
            # Convert American odds to decimal and calculate implied probabilities
            home_odd = float(odds[0].text.replace('+', ''))
            draw_odd = float(odds[1].text.replace('+', ''))
            away_odd = float(odds[2].text.replace('+', ''))

            # Calculate implied probabilities using the new formula
            implied_home_prob = implied_probability(home_odd) * 100
            implied_draw_prob = implied_probability(draw_odd) * 100
            implied_away_prob = implied_probability(away_odd) * 100

            # Total implied probability for normalization
            total_implied_prob = implied_home_prob + implied_draw_prob + implied_away_prob

            # Normalize probabilities to sum to 100%
            home_win_prob.append(round((implied_home_prob / total_implied_prob) * 100, 2))
            draw_prob.append(round((implied_draw_prob / total_implied_prob) * 100, 2))
            away_win_prob.append(round((implied_away_prob / total_implied_prob) * 100, 2))

            # Store decimal odds
            home_win_odds.append(american_to_decimal(home_odd))
            draw_odds.append(american_to_decimal(draw_odd))
            away_win_odds.append(american_to_decimal(away_odd))
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

# Save the DataFrame as a CSV file
df.sort_values(by='Game', ascending=True, inplace=True)
df.to_csv('betmgm_odds_with_normalized_probabilities.csv', index=False)
print("Data saved to 'betmgm_odds_with_normalized_probabilities.csv'")
