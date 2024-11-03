import pandas as pd
import requests
from bs4 import BeautifulSoup
import schedule
import time


def clean_odds(odds_text):
    # Remove any non-numeric characters (like commas or whitespace)
    cleaned_text = ''.join(filter(str.isdigit, odds_text))
    return int(cleaned_text) if cleaned_text else None


def american_odds_to_probability(odds):
    """Convert American odds to implied probability."""
    odds = int(odds)
    if odds > 0:  # Positive American odds
        probability = 100 / (odds + 100)
    else:  # Negative American odds
        probability = -odds / (-odds + 100)
    return probability


def normalize_probabilities(probabilities):
    """Normalize a list of probabilities to sum to 1 (or 100%)."""
    total_probability = sum(probabilities)
    return [p / total_probability for p in probabilities]


def scrape_betting_data():
    # DraftKings Premier League URL
    url = 'https://sportsbook.draftkings.com/leagues/soccer/england---premier-league'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Sending an HTTP request to the website
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200 means OK)
    if response.status_code == 200:
        print("Successfully fetched the website!")
    else:
        print(
            f"Failed to retrieve the page. Status code: {response.status_code}")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all match containers (divs with class 'sportsbook-event-accordion__wrapper')
    matches = soup.find_all(
        'div', class_='sportsbook-event-accordion__wrapper')

    # Extract information for each match
    data = []
    for match in matches:
        # Find the teams (they seem to be inside <a> tags with the class 'sportsbook-event-accordion__title')
        teams = match.find(
            'a', class_='sportsbook-event-accordion__title').text.strip()

        # Find the odds (e.g., stored inside spans or other tags)
        # Update the class if necessary
        odds_elements = match.find_all('span', class_='sportsbook-odds')
        if len(odds_elements) >= 3:
            try:

                # Convert odds to integers
                team1_odds = clean_odds(odds_elements[0].text.strip())
                draw_odds = clean_odds(odds_elements[1].text.strip())
                team2_odds = clean_odds(odds_elements[2].text.strip())

                # Convert American odds to implied probabilities
                team1_prob = american_odds_to_probability(team1_odds)
                draw_prob = american_odds_to_probability(draw_odds)
                team2_prob = american_odds_to_probability(team2_odds)

                # Normalize the probabilities
                normalized_probs = normalize_probabilities(
                    [team1_prob, draw_prob, team2_prob])

                # Append the result to the data list
                data.append([teams, team1_odds, draw_odds,
                            team2_odds] + normalized_probs)
            except ValueError:
                # Handle the case where odds are not valid integers
                data.append([teams, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
        else:
            data.append([teams, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])

    # Store data in a DataFrame and output
    df = pd.DataFrame(data, columns=['Match', 'Team 1 Odds', 'Draw Odds', 'Team 2 Odds',
                      'Normalized Team 1 Prob', 'Normalized Draw Prob', 'Normalized Team 2 Prob'])
    print(df)

    # Save to CSV
    df.to_csv('data/betting_data.csv', index=False)

    print("Data scraped and saved!")


#! Run once:
scrape_betting_data()

#! Run every 5 minutes
# # Schedule the function to run every 5 minutes
# schedule.every(5).minutes.do(scrape_betting_data)

# # Run the schedule in an infinite loop
# while True:
#     schedule.run_pending()
#     time.sleep(1)
