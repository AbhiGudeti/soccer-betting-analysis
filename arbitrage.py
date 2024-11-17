import pandas as pd


def normalize_team_name(team_name):
    """Normalize team names if necessary."""
    # Assuming team names are already normalized in your combined CSV
    return team_name.strip()


def find_arbitrage_opportunities(df_combined):
    arbitrage_opportunities = []

    # Iterate over each match
    for idx, row in df_combined.iterrows():
        home_team = row['Home Team']
        away_team = row['Away Team']
        match = f"{home_team} vs {away_team}"

        # Collect available odds from different bookmakers
        odds_home = {
            'draftkings': row.get('Home Win Probability_draftkings'),
            'pinnacle': row.get('Home Win Probability_pinnacle'),
            'betmgm': row.get('Home Win Probability_betmgm')
        }
        odds_draw = {
            'draftkings': row.get('Draw Probability_draftkings'),
            'pinnacle': row.get('Draw Probability_pinnacle'),
            'betmgm': row.get('Draw Probability_betmgm')
        }
        odds_away = {
            'draftkings': row.get('Away Win Probability_draftkings'),
            'pinnacle': row.get('Away Win Probability_pinnacle'),
            'betmgm': row.get('Away Win Probability_betmgm')
        }

        # Remove NaN values
        odds_home = {k: v for k, v in odds_home.items() if pd.notna(v)}
        odds_draw = {k: v for k, v in odds_draw.items() if pd.notna(v)}
        odds_away = {k: v for k, v in odds_away.items() if pd.notna(v)}

        # Ensure odds are numeric
        try:
            odds_home = {k: float(v) for k, v in odds_home.items()}
            odds_draw = {k: float(v) for k, v in odds_draw.items()}
            odds_away = {k: float(v) for k, v in odds_away.items()}
        except ValueError:
            continue  # Skip this row if conversion fails

        # Generate all combinations of odds from different bookmakers
        for bookmaker_home, odd_home in odds_home.items():
            for bookmaker_draw, odd_draw in odds_draw.items():
                for bookmaker_away, odd_away in odds_away.items():
                    # Calculate arbitrage percentage
                    arbitrage_percentage = (
                        100/odd_home) + (100/odd_draw) + (100/odd_away)
                    if arbitrage_percentage < 100:
                        arbitrage_opportunities.append({
                            'Match': match,
                            'Home Bookmaker': bookmaker_home,
                            'Home Odds': odd_home,
                            'Draw Bookmaker': bookmaker_draw,
                            'Draw Odds': odd_draw,
                            'Away Bookmaker': bookmaker_away,
                            'Away Odds': odd_away,
                            'Arbitrage Percentage': round(arbitrage_percentage * 100, 2)
                        })

    # Create a DataFrame for arbitrage opportunities
    df_arbitrage = pd.DataFrame(arbitrage_opportunities)
    return df_arbitrage


def main():
    # Read the combined data from the CSV file
    df_combined = pd.read_csv('combined_betting_data.csv')

    # Ensure team names are normalized (if not already)
    df_combined['Home Team'] = df_combined['Home Team'].apply(
        normalize_team_name)
    df_combined['Away Team'] = df_combined['Away Team'].apply(
        normalize_team_name)

    # Find arbitrage opportunities
    df_arbitrage = find_arbitrage_opportunities(df_combined)

    if not df_arbitrage.empty:
        print("Arbitrage opportunities found:")
        print(df_arbitrage)
        # Optionally, save to CSV
        df_arbitrage.to_csv('arbitrage_opportunities.csv', index=False)
        print("Arbitrage opportunities saved to 'arbitrage_opportunities.csv'")
    else:
        print("No arbitrage opportunities found.")


if __name__ == "__main__":
    main()
