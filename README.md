# Soccer Betting Odds Comparison Dashboard
## Project Overview
This project aims to create a real-time web dashboard that compares live soccer betting odds across several prominent bookmakers to determine which bets have the highest probability of hitting. The system scrapes live odds from different betting platforms and provides analysis to help users make informed decisions based on odds fluctuations.

Supported Bookmakers:
DraftKings
FanDuel Sportsbook
Pinnacle
## Project Phases
1. Web Scraping (1-2 weeks)
Build scripts to scrape the 1x2 match odds for live soccer matches from multiple bookmakers.
Tools: Python (BeautifulSoup, Selenium), API integrations (if available)
2. Data Cleaning (3-4 weeks)
Clean and preprocess the scraped data for analysis.
Ensure uniformity across bookmakers (e.g., team names, odds formatting).
Handle missing data, duplicates, and anomalies.
3. Exploratory Data Analysis (EDA) (1-2 weeks)
Visualize key betting insights (odds distribution, trends, outliers).
Analyze and compare odds across bookmakers to spot value bets.
4. Dashboard Development
Build an intuitive web interface to display live odds comparison and analytics.
Display key metrics such as expected value, odds fluctuations, and probability estimates.
Tools: Python (Flask/Django), JavaScript (React, D3.js)
## How It Works
Live Odds Scraping: Python scripts continuously scrape live betting odds from supported bookmakers.
Data Processing: The scraped odds are cleaned, standardized, and stored in a central database.
Analysis: The system evaluates which bets offer the best value, considering odds fluctuations and probabilities.
Web Dashboard: The processed data is displayed on an interactive dashboard for users to easily view and compare odds from different bookmakers.
Technologies Used
Backend:

Python (for web scraping and data processing)
Pandas, NumPy (for data cleaning and analysis)
Flask/Django (for backend server and API)
Frontend:

React.js (for web interface)
D3.js (for data visualization)

Database:

MongoDB/PostgreSQL (to store scraped odds)

Other Tools:
BeautifulSoup/Selenium (for web scraping)
