import yfinance as yf
import pandas as pd
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json

# Download VADER lexicon for sentiment analysis
nltk.download('vader_lexicon')

# Initialize the VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

# Function to fetch real-time prices and market cap for each stock
def get_real_time_data(stock):
    try:
        ticker = yf.Ticker(stock)
        hist = ticker.history(period='1d')
        market_cap = ticker.info.get('marketCap', None)
        price = hist['Close'].iloc[0] if not hist.empty else None
        return {'stock': stock, 'price': price, 'market_cap': market_cap}
    except Exception as e:
        print(f"Error fetching data for {stock}: {e}")
        return {'stock': stock, 'price': None, 'market_cap': None}

# Function to fetch stock information based on user input
def fetch_stock_info(stock, market_cap_bins, market_cap_labels):
    try:
        ticker = yf.Ticker(stock)
        info = ticker.info
        market_cap_category = pd.cut([info['marketCap']], bins=market_cap_bins, labels=market_cap_labels)[0]
        return {'stock': stock, 'price': info['previousClose'], 'market_cap': info['marketCap'], 'market_cap_category': market_cap_category}
    except Exception as e:
        return f"Error fetching data for {stock}: {e}"

# Function to get news articles
def get_news_articles(api_key, query, from_date, to_date, language='en'):
    url = (
        f'https://newsapi.org/v2/everything?q={query}&from={from_date}&to={to_date}&language={language}&apiKey={api_key}'
    )
    response = requests.get(url)
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"Error decoding JSON response for {query}.")
            return None
    else:
        print(f"Failed to fetch news articles for {query}: {response.status_code} - {response.text}")
        return None

# Function to analyze sentiment of the news articles
def analyze_sentiment(articles):
    sentiment_scores = {'positive': 0, 'neutral': 0, 'negative': 0}
    for article in articles:
        title = article.get('title', "")
        description = article.get('description', "")
        text = title + ". " + description
        sentiment = sid.polarity_scores(text)
        if sentiment['compound'] >= 0.05:
            sentiment_scores['positive'] += 1
        elif sentiment['compound'] <= -0.05:
            sentiment_scores['negative'] += 1
        else:
            sentiment_scores['neutral'] += 1
    return sentiment_scores

# API key for newsapi.org
api_key = 'cc07d16584a547ceb66428c133044b6e'

# User input for stock ticker symbol and date range
user_stock = input("Enter a stock ticker symbol: ").upper()
from_date = input("Enter the start date for sentiment analysis (YYYY-MM-DD): ")
to_date = input("Enter the end date for sentiment analysis (YYYY-MM-DD): ")

# Get the real-time data for the provided stock
real_time_data = get_real_time_data(user_stock)

# Define the ranges for categorization based on market cap
market_cap_bins = [0, 2e9, 10e9, float('inf')]  # Adjust these ranges as needed
market_cap_labels = ['Small Cap', 'Mid Cap', 'Large Cap']

# Fetch detailed stock information
stock_info = fetch_stock_info(user_stock, market_cap_bins, market_cap_labels)

# Display stock information
if isinstance(stock_info, dict):
    print(f"\nStock: {stock_info['stock']}")
    print(f"Price: ${stock_info['price']:.2f}")
    print(f"Market Cap: ${stock_info['market_cap']:,}")
    print(f"Category: {stock_info['market_cap_category']}")
else:
    print(stock_info)

# Fetch and analyze news articles
news_data = get_news_articles(api_key, user_stock, from_date, to_date)

if news_data and news_data.get('status') == 'ok':
    articles = news_data.get('articles', [])
    sentiment_scores = analyze_sentiment(articles)
    total_articles = len(articles)
    
    print(f"\nSentiment Analysis for {user_stock} from {from_date} to {to_date}")
    print(f"Total articles analyzed: {total_articles}")
    print(f"Positive sentiment: {sentiment_scores['positive']} ({(sentiment_scores['positive']/total_articles)*100:.2f}%)")
    print(f"Neutral sentiment: {sentiment_scores['neutral']} ({(sentiment_scores['neutral']/total_articles)*100:.2f}%)")
    print(f"Negative sentiment: {sentiment_scores['negative']} ({(sentiment_scores['negative']/total_articles)*100:.2f}%)")
else:
    print(f"No news articles found for {user_stock} or failed to fetch the news data.")
