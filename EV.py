import pandas as pd


def find_most_profitable_matches(df_ev):
    """
    Sort matches by the most profitable expected value for each outcome
    and generate a new CSV file.
    """
    # Group by match and find the maximum EV for each match
    df_sorted = df_ev.sort_values(
        by='Expected Value', ascending=False).reset_index(drop=True)

    # Save to a new CSV file
    df_sorted.to_csv('most_profitable_matches.csv', index=False)
    print("Most profitable matches saved to 'most_profitable_matches.csv'")

    return df_sorted


def convert_american_to_decimal(odds):
    """Convert American odds to decimal odds."""
    if odds > 0:
        return (odds / 100) + 1
    else:
        return (100 / abs(odds)) + 1


def calculate_ev(probability, decimal_odds):
    """
    Calculate the Expected Value (EV).
    EV = (Probability of Outcome) * (Payout Odds) - (1 - Probability of Outcome)
    """
    probability = probability / 100  # Convert probability to decimal
    return (probability * decimal_odds) - (1 - probability)


def find_expected_values(df_combined):
    """
    Calculate expected values for all events across all bookmakers.
    """
    ev_results = []

    # Iterate over each match
    for idx, row in df_combined.iterrows():
        home_team = row['Home Team']
        away_team = row['Away Team']
        match = f"{home_team} vs {away_team}"

        # Extract probabilities and odds
        probabilities_odds = [
            ('draftkings', 'Home Win Probability_draftkings',
             'Home Win Odds_draftkings', 'american'),
            ('draftkings', 'Draw Probability_draftkings',
             'Draw Odds_draftkings', 'american'),
            ('draftkings', 'Away Win Probability_draftkings',
             'Away Win Odds_draftkings', 'american'),
            ('pinnacle', 'Home Win Probability_pinnacle',
             'Home Win Odds_pinnacle', 'decimal'),
            ('pinnacle', 'Draw Probability_pinnacle',
             'Draw Odds_pinnacle', 'decimal'),
            ('pinnacle', 'Away Win Probability_pinnacle',
             'Away Win Odds_pinnacle', 'decimal'),
            ('betmgm', 'Home Win Probability_betmgm',
             'Home Win Odds_betmgm', 'decimal'),
            ('betmgm', 'Draw Probability_betmgm', 'Draw Odds_betmgm', 'decimal'),
            ('betmgm', 'Away Win Probability_betmgm',
             'Away Win Odds_betmgm', 'decimal')
        ]

        for bookmaker, prob_col, odds_col, odds_type in probabilities_odds:
            try:
                probability = row.get(prob_col)
                odds = row.get(odds_col)

                if pd.notna(probability) and pd.notna(odds):
                    # Convert American odds to decimal odds if necessary
                    if odds_type == 'american':
                        odds = convert_american_to_decimal(odds)

                    # Calculate EV
                    ev = calculate_ev(probability, odds)

                    # Store results
                    ev_results.append({
                        'Match': match,
                        'Bookmaker': bookmaker,
                        # Home, Draw, or Away
                        'Outcome': prob_col.split(' ')[0],
                        'Probability (%)': round(probability, 2),
                        'Odds (Decimal)': round(odds, 2),
                        'Expected Value': round(ev, 2)
                    })
            except Exception as e:
                print(f"Error calculating EV for {match} at {bookmaker}: {e}")

    # Create a DataFrame for expected values
    df_ev = pd.DataFrame(ev_results)
    return df_ev


def main():
    # Read the combined data from the CSV file
    df_combined = pd.read_csv('combined_betting_data.csv')

    # Find expected values
    df_ev = find_expected_values(df_combined)

    if not df_ev.empty:
        print("Expected values calculated:")
        print(df_ev)

        # Save EVs to CSV
        df_ev.to_csv('expected_values.csv', index=False)
        print("Expected values saved to 'expected_values.csv'")

        # Sort by most profitable matches
        df_sorted = find_most_profitable_matches(df_ev)

        print("Most profitable matches sorted:")
        print(df_sorted.head())  # Display the top 5 profitable matches
    else:
        print("No expected values could be calculated.")


if __name__ == "__main__":
    main()
