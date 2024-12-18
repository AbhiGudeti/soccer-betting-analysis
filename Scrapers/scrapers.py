from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait

# Shared TEAM_NAME_MAPPING
TEAM_NAME_MAPPING = {
    "Man Utd": "Manchester United",
    "Man United": "Manchester United",
    "Manchester United": "Manchester United",
    "Chelsea": "Chelsea",
    "Fulham": "Fulham",
    "Brentford": "Brentford",
    "West Ham": "West Ham United",
    "West Ham United": "West Ham United",
    "Everton": "Everton",
    "Everton FC": "Everton",
    "Wolves": "Wolverhampton Wanderers",
    "Wolverhampton Wanderers": "Wolverhampton Wanderers",
    "Southampton": "Southampton",
    "Southampton FC": "Southampton",
    "Crystal Palace": "Crystal Palace",
    "Bournemouth": "AFC Bournemouth",
    "AFC Bournemouth": "AFC Bournemouth",
    "Brighton": "Brighton & Hove Albion",
    "Brighton and Hove Albion": "Brighton & Hove Albion",
    "Brighton & Hove Albion": "Brighton & Hove Albion",
    "Man City": "Manchester City",
    "Manchester City": "Manchester City",
    "Liverpool": "Liverpool",
    "Aston Villa": "Aston Villa",
    "Tottenham": "Tottenham Hotspur",
    "Tottenham Hotspur": "Tottenham Hotspur",
    "Ipswich": "Ipswich Town",
    "Ipswich Town": "Ipswich Town",
    "Leicester": "Leicester City",
    "Leicester City": "Leicester City",
    "Nottingham Forest": "Nottingham Forest",
    "Newcastle": "Newcastle United",
    "Newcastle United": "Newcastle United",
    "Arsenal": "Arsenal"
}

def normalize_team_name(team_name):
    """Normalize team names using the TEAM_NAME_MAPPING dictionary."""
    normalized_name = team_name.strip()
    return TEAM_NAME_MAPPING.get(normalized_name, normalized_name)

def clean_odds(odds_text):
    # Remove any non-numeric characters (like commas or whitespace)
    cleaned_text = ''.join(
        filter(lambda x: x.isdigit() or x == '-' or x == '+', odds_text))
    return int(cleaned_text) if cleaned_text else None

def american_odds_to_probability(odds):
    """Convert American odds to implied probability."""
    odds = int(odds)
    if odds > 0:  # Positive American odds
        probability = 100 / (odds + 100)
    else:  # Negative American odds
        probability = -odds / (-odds + 100)
    return probability * 100  # Return as percentage

def normalize_probabilities(probabilities):
    """Normalize a list of probabilities to sum to 100%."""
    total_probability = sum(probabilities)
    return [p / total_probability * 100 for p in probabilities]

def scrape_draftkings():
    # DraftKings Premier League URL
    url = 'https://sportsbook.draftkings.com/leagues/soccer/england---premier-league'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    }

    # Sending an HTTP request to the website
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(
            f"Failed to retrieve DraftKings page. Status code: {response.status_code}")
        return pd.DataFrame()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all match containers
    matches = soup.find_all(
        'div', class_='sportsbook-event-accordion__wrapper')

    # Extract information for each match
    data = []
    for match in matches:
        # Find the teams
        teams = match.find(
            'a', class_='sportsbook-event-accordion__title').text.strip()

        # Split and normalize the team names
        team_names = teams.split("vs")
        if len(team_names) == 2:
            home_team = normalize_team_name(team_names[0].strip())
            away_team = normalize_team_name(team_names[1].strip())
        else:
            continue  # Skip if the team names are not in expected format

        # Find the odds
        odds_elements = match.find_all('span', class_='sportsbook-odds')
        if len(odds_elements) >= 3:
            try:
                # Clean and convert odds to integers
                home_odds = clean_odds(odds_elements[0].text.strip())
                draw_odds = clean_odds(odds_elements[1].text.strip())
                away_odds = clean_odds(odds_elements[2].text.strip())

                # Convert American odds to implied probabilities
                home_prob = american_odds_to_probability(home_odds)
                draw_prob = american_odds_to_probability(draw_odds)
                away_prob = american_odds_to_probability(away_odds)

                # Normalize the probabilities
                normalized_probs = normalize_probabilities(
                    [home_prob, draw_prob, away_prob])

                # Append the result to the data list
                data.append([
                    home_team,
                    away_team,
                    home_odds,
                    draw_odds,
                    away_odds,
                    normalized_probs[0],
                    normalized_probs[1],
                    normalized_probs[2]
                ])
            except ValueError:
                # Handle invalid odds
                continue
        else:
            continue  # Skip if odds are missing

    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'Home Team',
        'Away Team',
        'Home Win Odds',
        'Draw Odds',
        'Away Win Odds',
        'Home Win Probability',
        'Draw Probability',
        'Away Win Probability'
    ])

    # Remove duplicates and sort
    df.drop_duplicates(inplace=True)
    df.sort_values(by=['Home Team'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(df)
    return df

def scrape_pinnacle():
    # Setup Selenium
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    # URL of the Pinnacle page with odds
    url = "https://www.pinnacle.com/en/soccer/england-premier-league/matchups/#all"
    driver.get(url)

    # Wait for the game rows to load
    time.sleep(5)  # Adjust as needed

    # Lists to store data
    home_teams = []
    away_teams = []
    home_win_odds = []
    draw_odds = []
    away_win_odds = []
    home_win_prob = []
    draw_prob = []
    away_win_prob = []

    # Locate each game row
    game_rows = WebDriverWait(driver, 100).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div.row-u9F3b9WCM3.row-k9ktBvvTsJ'))
    )
    print(f"Pinnacle: Found {len(game_rows)} game rows")  # Debugging statement

    for row in game_rows:
        try:
            # Extract team names
            teams = row.find_elements(
                By.CSS_SELECTOR, 'div.gameInfoLabel-EDDYv5xEfd span')

            if len(teams) >= 2:
                home_team = teams[0].text.replace("(Match)", "").strip()
                away_team = teams[1].text.replace("(Match)", "").strip()

                # Handle cases where away_team might be a number
                if away_team.isdigit():
                    if len(teams) >= 3:
                        away_team = teams[2].text.replace(
                            "(Match)", "").strip()
                    else:
                        away_team = None

                # Normalize team names
                home_team = normalize_team_name(home_team)
                away_team = normalize_team_name(away_team)

                print(f"Game: {home_team} vs {away_team}")  # For debugging

                # Append to team lists
                home_teams.append(home_team)
                away_teams.append(away_team)
            else:
                continue  # Skip if team names are not found

            # Extract odds
            odds = row.find_elements(By.CSS_SELECTOR, 'span.price-r5BU0ynJha')
            # Debugging statement
            print(f"Odds found: {[odd.text for odd in odds]}")
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
                fair_home_prob = round(
                    (home_prob / total_implied_prob) * 100, 2)
                fair_draw_prob = round(
                    (draw_prob_value / total_implied_prob) * 100, 2)
                fair_away_prob = round(
                    (away_prob / total_implied_prob) * 100, 2)

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
        'Home Team': home_teams,
        'Away Team': away_teams,
        'Home Win Odds': home_win_odds,
        'Draw Odds': draw_odds,
        'Away Win Odds': away_win_odds,
        'Home Win Probability': home_win_prob,
        'Draw Probability': draw_prob,
        'Away Win Probability': away_win_prob
    })

    # Remove duplicates and sort
    df.drop_duplicates(inplace=True)
    df.sort_values(by=['Home Team'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Print DataFrame content for debugging
    print(df)

    # Return the DataFrame
    return df

def scrape_betmgm():
    # Setup Selenium
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    # URL of the page
    url = "https://sports.nj.betmgm.com/en/sports/soccer-4/betting/england-14?tab=matches"
    driver.get(url)

    # Wait for content to load
    time.sleep(5)  # Adjust as necessary

    # Lists to store data
    data = []

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
    print(f"BetMGM: Found {len(game_rows)} game rows")  # Debugging statement

    for row in game_rows:
        try:
            # Extract team names
            teams = row.find_elements(
                By.CSS_SELECTOR, 'div.participant-info .participant')
            if len(teams) >= 2:
                home_team = normalize_team_name(teams[0].text.strip())
                away_team = normalize_team_name(teams[1].text.strip())
            else:
                continue  # Skip if team names are not found

            # Extract odds
            odds = row.find_elements(
                By.CSS_SELECTOR, 'span.custom-odds-value-style')
            if len(odds) >= 3:
                # Convert American odds to decimal and calculate implied probabilities
                home_odd_text = odds[0].text.replace(
                    '+', '').replace('½', '.5')
                draw_odd_text = odds[1].text.replace(
                    '+', '').replace('½', '.5')
                away_odd_text = odds[2].text.replace(
                    '+', '').replace('½', '.5')

                home_odd = float(home_odd_text)
                draw_odd = float(draw_odd_text)
                away_odd = float(away_odd_text)

                # Calculate implied probabilities
                implied_home_prob = implied_probability(home_odd) * 100
                implied_draw_prob = implied_probability(draw_odd) * 100
                implied_away_prob = implied_probability(away_odd) * 100

                # Total implied probability for normalization
                total_implied_prob = implied_home_prob + implied_draw_prob + implied_away_prob

                # Normalize probabilities to sum to 100%
                fair_home_prob = round(
                    (implied_home_prob / total_implied_prob) * 100, 2)
                fair_draw_prob = round(
                    (implied_draw_prob / total_implied_prob) * 100, 2)
                fair_away_prob = round(
                    (implied_away_prob / total_implied_prob) * 100, 2)

                # Store decimal odds
                home_decimal_odds = american_to_decimal(home_odd)
                draw_decimal_odds = american_to_decimal(draw_odd)
                away_decimal_odds = american_to_decimal(away_odd)

                # Append data
                data.append([
                    home_team,
                    away_team,
                    home_decimal_odds,
                    draw_decimal_odds,
                    away_decimal_odds,
                    fair_home_prob,
                    fair_draw_prob,
                    fair_away_prob
                ])
            else:
                continue  # Skip if odds are missing
        except Exception as e:
            print(f"Error extracting data for a row: {e}")
            continue

    # Close the browser
    driver.quit()

    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'Home Team',
        'Away Team',
        'Home Win Odds',
        'Draw Odds',
        'Away Win Odds',
        'Home Win Probability',
        'Draw Probability',
        'Away Win Probability'
    ])

    # Remove duplicates and sort
    df.drop_duplicates(inplace=True)
    df.sort_values(by=['Home Team'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    print(df)

    return df

def main():
    # Get dataframes from each source
    df_draftkings = scrape_draftkings()
    df_pinnacle = scrape_pinnacle()
    df_betmgm = scrape_betmgm()

    # Check if DataFrames are not empty
    if df_draftkings.empty or df_pinnacle.empty or df_betmgm.empty:
        print("One or more data sources did not return any data. Exiting.")
        return

    # Rename columns to include source
    df_draftkings.rename(columns={
        'Home Win Odds': 'Home Win Odds_draftkings',
        'Draw Odds': 'Draw Odds_draftkings',
        'Away Win Odds': 'Away Win Odds_draftkings',
        'Home Win Probability': 'Home Win Probability_draftkings',
        'Draw Probability': 'Draw Probability_draftkings',
        'Away Win Probability': 'Away Win Probability_draftkings'
    }, inplace=True)

    df_pinnacle.rename(columns={
        'Home Win Odds': 'Home Win Odds_pinnacle',
        'Draw Odds': 'Draw Odds_pinnacle',
        'Away Win Odds': 'Away Win Odds_pinnacle',
        'Home Win Probability': 'Home Win Probability_pinnacle',
        'Draw Probability': 'Draw Probability_pinnacle',
        'Away Win Probability': 'Away Win Probability_pinnacle'
    }, inplace=True)

    df_betmgm.rename(columns={
        'Home Win Odds': 'Home Win Odds_betmgm',
        'Draw Odds': 'Draw Odds_betmgm',
        'Away Win Odds': 'Away Win Odds_betmgm',
        'Home Win Probability': 'Home Win Probability_betmgm',
        'Draw Probability': 'Draw Probability_betmgm',
        'Away Win Probability': 'Away Win Probability_betmgm'
    }, inplace=True)

    # Merge dataframes on 'Home Team' and 'Away Team' using inner joins
    df_merged = pd.merge(df_draftkings, df_pinnacle, on=['Home Team', 'Away Team'], how='inner')
    df_merged = pd.merge(df_merged, df_betmgm, on=['Home Team', 'Away Team'], how='inner')

    # Check if the merged DataFrame is empty
    if df_merged.empty:
        print("No common games found across all three websites.")
        return

    # Ensure that odds and probabilities columns are numeric
    odds_columns = [
        'Home Win Odds_draftkings', 'Draw Odds_draftkings', 'Away Win Odds_draftkings',
        'Home Win Odds_pinnacle', 'Draw Odds_pinnacle', 'Away Win Odds_pinnacle',
        'Home Win Odds_betmgm', 'Draw Odds_betmgm', 'Away Win Odds_betmgm'
    ]

    probability_columns = [
        'Home Win Probability_draftkings', 'Draw Probability_draftkings', 'Away Win Probability_draftkings',
        'Home Win Probability_pinnacle', 'Draw Probability_pinnacle', 'Away Win Probability_pinnacle',
        'Home Win Probability_betmgm', 'Draw Probability_betmgm', 'Away Win Probability_betmgm'
    ]

    # Convert columns to numeric, coercing errors to NaN
    for col in odds_columns + probability_columns:
        df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')

    # Calculate average odds
    df_merged['Average Home Win Odds'] = df_merged[
        ['Home Win Odds_draftkings', 'Home Win Odds_pinnacle', 'Home Win Odds_betmgm']
    ].mean(axis=1, skipna=True)

    df_merged['Average Draw Odds'] = df_merged[
        ['Draw Odds_draftkings', 'Draw Odds_pinnacle', 'Draw Odds_betmgm']
    ].mean(axis=1, skipna=True)

    df_merged['Average Away Win Odds'] = df_merged[
        ['Away Win Odds_draftkings', 'Away Win Odds_pinnacle', 'Away Win Odds_betmgm']
    ].mean(axis=1, skipna=True)

    # Calculate average probabilities
    df_merged['Average Home Win Probability'] = df_merged[
        ['Home Win Probability_draftkings', 'Home Win Probability_pinnacle', 'Home Win Probability_betmgm']
    ].mean(axis=1, skipna=True)

    df_merged['Average Draw Probability'] = df_merged[
        ['Draw Probability_draftkings', 'Draw Probability_pinnacle', 'Draw Probability_betmgm']
    ].mean(axis=1, skipna=True)

    df_merged['Average Away Win Probability'] = df_merged[
        ['Away Win Probability_draftkings', 'Away Win Probability_pinnacle', 'Away Win Probability_betmgm']
    ].mean(axis=1, skipna=True)

    # Round all numerical columns to two decimal places
    numeric_columns = odds_columns + probability_columns + [
        'Average Home Win Odds', 'Average Draw Odds', 'Average Away Win Odds',
        'Average Home Win Probability', 'Average Draw Probability', 'Average Away Win Probability'
    ]
    df_merged[numeric_columns] = df_merged[numeric_columns].round(2)

    # Save the combined dataframe to CSV
    df_merged.to_csv('combined_betting_data.csv', index=False)
    print("Data saved to 'combined_betting_data.csv'")

if __name__ == "__main__":
    main()