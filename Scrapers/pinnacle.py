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
options.headless = False  # Set to False for visible browser window
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# URL of the Pinnacle page with odds
url = "https://www.pinnacle.com/en/soccer/england-premier-league/matchups/#all"
driver.get(url)

# Wait for the game rows to load
time.sleep(5)  # Basic wait for content to load; adjust as needed

# Lists to store data
games = []
home_win_odds = []
draw_odds = []
away_win_odds = []
home_win_prob = []
draw_prob = []
away_win_prob = []

# Locate each game row
game_rows = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.row-u9F3b9WCM3.row-k9ktBvvTsJ'))
)
print(f"Found {len(game_rows)} game rows")  # Debugging statement

for row in game_rows:
    try:
        # Extract team names
        teams = row.find_elements(By.CSS_SELECTOR, 'div.gameInfoLabel-EDDYv5xEfd span')

        TEAM_NAME_MAPPING = {
            "Manchester United": "Manchester United",
            "Chelsea": "Chelsea",
            "Fulham": "Fulham",
            "Brentford": "Brentford",
            "West Ham United": "West Ham United",
            "Everton": "Everton",
            "Wolves": "Wolverhampton Wanderers",
            "Southampton": "Southampton",
            "Crystal Palace": "Crystal Palace",
            "Bournemouth": "AFC Bournemouth",
            "Brighton and Hove Albion": "Brighton & Hove Albion",
            "Manchester City": "Manchester City",
            "Liverpool": "Liverpool",
            "Aston Villa": "Aston Villa",
            "Tottenham Hotspur": "Tottenham Hotspur",
            "Ipswich Town": "Ipswich Town",
            "Leicester City": "Leicester City",
            "Nottingham Forest": "Nottingham Forest",
            "Newcastle United": "Newcastle United",
            "Arsenal": "Arsenal"
        }

        if len(teams) >= 2:
            home_team = teams[0].text.replace("(Match)", "")
            away_team = teams[1].text
            if isinstance(away_team, str):
                away_team = teams[1].text.replace("(Match)", "")
            elif isinstance(int(away_team), int):
                away_team = teams[2].text.replace("(Match)", "")

            def normalize_team_name(team_name):
                """Normalize team names using the TEAM_NAME_MAPPING dictionary."""
                # Strip any extra whitespace and use the dictionary to normalize
                normalized_name = team_name.strip()
                return TEAM_NAME_MAPPING.get(normalized_name, normalized_name)

            team1 = normalize_team_name(home_team.strip())
            team2 = normalize_team_name(away_team.strip())

            game_name = f"{team1} vs {team2}"
            games.append(game_name)
            print(f"Game: {game_name}")  # For debugging


        # Extract odds
        odds = row.find_elements(By.CSS_SELECTOR, 'span.price-r5BU0ynJha')
        print(f"Odds found: {[odd.text for odd in odds]}")  # Debugging statement
        if len(odds) >= 3:
            # Convert odds to float and calculate implied probabilities
            home_odds = float(odds[0].text)
            draw_odds_value = float(odds[1].text)
            away_odds = float(odds[2].text)
            
            home_win_odds.append(home_odds)
            draw_odds.append(draw_odds_value)
            away_win_odds.append(away_odds)
            
            # Calculate initial implied probabilities
            home_prob = (1 / home_odds) * 100
            draw_prob_value = (1 / draw_odds_value) * 100
            away_prob = (1 / away_odds) * 100

            # Calculate total implied probability (overround)
            total_implied_prob = home_prob + draw_prob_value + away_prob

            # Adjust each probability to remove overround
            fair_home_prob = round((home_prob / total_implied_prob) * 100, 2)
            fair_draw_prob = round((draw_prob_value / total_implied_prob) * 100, 2)
            fair_away_prob = round((away_prob / total_implied_prob) * 100, 2)

            # Append adjusted probabilities
            home_win_prob.append(fair_home_prob)
            draw_prob.append(fair_draw_prob)
            away_win_prob.append(fair_away_prob)
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

df.sort_values(by='Game', inplace=True)

# Print DataFrame content for debugging
print(df)

# Save the DataFrame as a CSV file
df.to_csv('pinnacle_odds_with_probabilities.csv', index=False)
print("Data saved to 'pinnacle_odds_with_probabilities.csv'")