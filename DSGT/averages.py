import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from rapidfuzz import process, fuzz

# Standard list of Premier League team names
standard_team_names = [
    'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton & Hove Albion', 'Burnley', 'Chelsea',
    'Crystal Palace', 'Everton', 'Fulham', 'Liverpool', 'Luton Town', 'Manchester City',
    'Manchester United', 'Newcastle United', 'Nottingham Forest', 'Sheffield United',
    'Tottenham Hotspur', 'West Ham United', 'Wolverhampton Wanderers'
]

# Function to standardize team names using fuzzy matching
def standardize_team_name(name):
    match = process.extractOne(name, standard_team_names, scorer=fuzz.token_sort_ratio)
    if match and match[1] >= 70:  # Threshold for matching
        return match[0]
    else:
        return name  # Return original name if no good match found

# Function to scrape Pinnacle
def get_pinnacle_data(driver):
    url = "https://www.pinnacle.com/en/soccer/england-premier-league/matchups/#all"
    driver.get(url)
    time.sleep(5)
    
    home_teams = []
    away_teams = []
    home_win_odds = []
    draw_odds = []
    away_win_odds = []
    home_win_prob = []
    draw_prob = []
    away_win_prob = []
    
    game_rows = driver.find_elements(By.CSS_SELECTOR, 'div.row-u9F3b9WCM3.row-k9ktBvvTsJ')
    for row in game_rows:
        try:
            teams = row.find_elements(By.CSS_SELECTOR, 'div.gameInfoLabel-EDDYv5xEfd span')
            if len(teams) >= 2:
                home_team = standardize_team_name(teams[0].text)
                away_team = standardize_team_name(teams[1].text)
                home_teams.append(home_team)
                away_teams.append(away_team)
            odds = row.find_elements(By.CSS_SELECTOR, 'span.price-r5BU0ynJha')
            if len(odds) >= 3:
                home_odds = float(odds[0].text)
                draw_odds_value = float(odds[1].text)
                away_odds = float(odds[2].text)
                home_win_odds.append(home_odds)
                draw_odds.append(draw_odds_value)
                away_win_odds.append(away_odds)
                home_win_prob.append(round((1 / home_odds) * 100, 2))
                draw_prob.append(round((1 / draw_odds_value) * 100, 2))
                away_win_prob.append(round((1 / away_odds) * 100, 2))
            else:
                home_win_odds.append(None)
                draw_odds.append(None)
                away_win_odds.append(None)
                home_win_prob.append(None)
                draw_prob.append(None)
                away_win_prob.append(None)
        except Exception:
            continue
    
    df_pinnacle = pd.DataFrame({
        'Home Team': home_teams,
        'Away Team': away_teams,
        'Home Win Odds': home_win_odds,
        'Draw Odds': draw_odds,
        'Away Win Odds': away_win_odds,
        'Home Win Probability': home_win_prob,
        'Draw Probability': draw_prob,
        'Away Win Probability': away_win_prob
    })
    return df_pinnacle

# Function to scrape DraftKings
def get_draftkings_data(driver):
    url = "https://sportsbook.draftkings.com/leagues/soccer/england---premier-league"
    driver.get(url)
    time.sleep(5)
    
    home_teams = []
    away_teams = []
    home_win_odds = []
    draw_odds = []
    away_win_odds = []
    home_win_prob = []
    draw_prob = []
    away_win_prob = []
    
    def american_to_decimal(odd):
        if odd > 0:
            return (odd / 100) + 1
        else:
            return (100 / abs(odd)) + 1
    
    game_rows = driver.find_elements(By.CSS_SELECTOR, '.sportsbook-event-accordion__wrapper')
    for row in game_rows:
        try:
            teams = row.find_elements(By.CSS_SELECTOR, 'a.sportsbook-event-accordion__title')
            if len(teams) == 1:
                game_name = teams[0].text
                # Split the game name to get home and away teams
                if ' @ ' in game_name:
                    away_team_raw, home_team_raw = game_name.split(' @ ')
                elif ' vs ' in game_name:
                    home_team_raw, away_team_raw = game_name.split(' vs ')
                else:
                    continue  # Unable to parse game name
                home_team = standardize_team_name(home_team_raw)
                away_team = standardize_team_name(away_team_raw)
                home_teams.append(home_team)
                away_teams.append(away_team)
            odds_elements = row.find_elements(By.CSS_SELECTOR, 'span.sportsbook-odds')
            if len(odds_elements) >= 3:
                home_odd_text = odds_elements[0].text.replace('−', '-').replace('+', '')
                draw_odd_text = odds_elements[1].text.replace('−', '-').replace('+', '')
                away_odd_text = odds_elements[2].text.replace('−', '-').replace('+', '')
                home_odds = american_to_decimal(float(home_odd_text))
                draw_odds_value = american_to_decimal(float(draw_odd_text))
                away_odds = american_to_decimal(float(away_odd_text))
                home_win_odds.append(home_odds)
                draw_odds.append(draw_odds_value)
                away_win_odds.append(away_odds)
                implied_home_prob = (1 / home_odds) * 100
                implied_draw_prob = (1 / draw_odds_value) * 100
                implied_away_prob = (1 / away_odds) * 100
                total_prob = implied_home_prob + implied_draw_prob + implied_away_prob
                home_win_prob.append(round((implied_home_prob / total_prob) * 100, 2))
                draw_prob.append(round((implied_draw_prob / total_prob) * 100, 2))
                away_win_prob.append(round((implied_away_prob / total_prob) * 100, 2))
            else:
                home_win_odds.append(None)
                draw_odds.append(None)
                away_win_odds.append(None)
                home_win_prob.append(None)
                draw_prob.append(None)
                away_win_prob.append(None)
        except Exception:
            continue
    
    df_draftkings = pd.DataFrame({
        'Home Team': home_teams,
        'Away Team': away_teams,
        'Home Win Odds': home_win_odds,
        'Draw Odds': draw_odds,
        'Away Win Odds': away_win_odds,
        'Home Win Probability': home_win_prob,
        'Draw Probability': draw_prob,
        'Away Win Probability': away_win_prob
    })
    return df_draftkings

# Function to scrape BetMGM
def get_betmgm_data(driver):
    url = "https://sports.nj.betmgm.com/en/sports/soccer-4"
    driver.get(url)
    time.sleep(5)
    
    home_teams = []
    away_teams = []
    home_win_odds = []
    draw_odds = []
    away_win_odds = []
    home_win_prob = []
    draw_prob = []
    away_win_prob = []
    
    def american_to_decimal(odd):
        if odd > 0:
            return (odd / 100) + 1
        else:
            return (100 / abs(odd)) + 1
    
    game_rows = driver.find_elements(By.CSS_SELECTOR, 'ms-event.grid-event')
    for row in game_rows:
        try:
            teams = row.find_elements(By.CSS_SELECTOR, 'div.participant-info .participant')
            if len(teams) >= 2:
                # Note: BetMGM may list teams in different order
                home_team_raw = teams[0].text
                away_team_raw = teams[1].text
                home_team = standardize_team_name(home_team_raw)
                away_team = standardize_team_name(away_team_raw)
                home_teams.append(home_team)
                away_teams.append(away_team)
            odds = row.find_elements(By.CSS_SELECTOR, 'span.custom-odds-value-style')
            if len(odds) >= 3:
                home_odd_text = odds[0].text.replace('−', '-').replace('+', '')
                draw_odd_text = odds[1].text.replace('−', '-').replace('+', '')
                away_odd_text = odds[2].text.replace('−', '-').replace('+', '')
                home_odds = american_to_decimal(float(home_odd_text))
                draw_odds_value = american_to_decimal(float(draw_odd_text))
                away_odds = american_to_decimal(float(away_odd_text))
                implied_home_prob = (1 / home_odds) * 100
                implied_draw_prob = (1 / draw_odds_value) * 100
                implied_away_prob = (1 / away_odds) * 100
                total_implied_prob = implied_home_prob + implied_draw_prob + implied_away_prob
                home_win_prob.append(round((implied_home_prob / total_implied_prob) * 100, 2))
                draw_prob.append(round((implied_draw_prob / total_implied_prob) * 100, 2))
                away_win_prob.append(round((implied_away_prob / total_implied_prob) * 100, 2))
                home_win_odds.append(home_odds)
                draw_odds.append(draw_odds_value)
                away_win_odds.append(away_odds)
            else:
                home_win_odds.append(None)
                draw_odds.append(None)
                away_win_odds.append(None)
                home_win_prob.append(None)
                draw_prob.append(None)
                away_win_prob.append(None)
        except Exception:
            continue
    
    df_betmgm = pd.DataFrame({
        'Home Team': home_teams,
        'Away Team': away_teams,
        'Home Win Odds': home_win_odds,
        'Draw Odds': draw_odds,
        'Away Win Odds': away_win_odds,
        'Home Win Probability': home_win_prob,
        'Draw Probability': draw_prob,
        'Away Win Probability': away_win_prob
    })
    return df_betmgm

# Main script
if __name__ == "__main__":
    # Setup Selenium
    options = Options()
    options.headless = False  # Set to True to run headless
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Scrape data from all three websites
    df_pinnacle = get_pinnacle_data(driver)
    df_draftkings = get_draftkings_data(driver)
    df_betmgm = get_betmgm_data(driver)
    
    # Close the browser
    driver.quit()
    
    # Merge dataframes on 'Home Team' and 'Away Team' columns
    df_combined = df_pinnacle.merge(df_draftkings, on=['Home Team', 'Away Team'], suffixes=('_pinnacle', '_draftkings'), how='outer')
    df_combined = df_combined.merge(df_betmgm, on=['Home Team', 'Away Team'], suffixes=('', '_betmgm'), how='outer')
    
    # Calculate average odds and probabilities
    df_combined['Average Home Win Odds'] = df_combined[['Home Win Odds_pinnacle', 'Home Win Odds_draftkings', 'Home Win Odds']].mean(axis=1)
    df_combined['Average Draw Odds'] = df_combined[['Draw Odds_pinnacle', 'Draw Odds_draftkings', 'Draw Odds']].mean(axis=1)
    df_combined['Average Away Win Odds'] = df_combined[['Away Win Odds_pinnacle', 'Away Win Odds_draftkings', 'Away Win Odds']].mean(axis=1)
    
    df_combined['Average Home Win Probability'] = df_combined[['Home Win Probability_pinnacle', 'Home Win Probability_draftkings', 'Home Win Probability']].mean(axis=1)
    df_combined['Average Draw Probability'] = df_combined[['Draw Probability_pinnacle', 'Draw Probability_draftkings', 'Draw Probability']].mean(axis=1)
    df_combined['Average Away Win Probability'] = df_combined[['Away Win Probability_pinnacle', 'Away Win Probability_draftkings', 'Away Win Probability']].mean(axis=1)
    
    # Select relevant columns
    df_final = df_combined[['Home Team', 'Away Team', 'Average Home Win Odds', 'Average Draw Odds', 'Average Away Win Odds',
                            'Average Home Win Probability', 'Average Draw Probability', 'Average Away Win Probability']]
    
    # Print the final DataFrame
    print(df_final)
    
    # Save to CSV
    df_final.to_csv('averaged_odds_and_probabilities.csv', index=False)
    print("Data saved to 'averaged_odds_and_probabilities.csv'")