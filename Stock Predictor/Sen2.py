import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json

# Download VADER lexicon for sentiment analysis
nltk.download('vader_lexicon')

# Initialize the VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

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

# User input for companies and date range
user_input = input("Enter company ticker symbols separated by commas (e.g., AAPL, MSFT, GOOGL): ")
companies = [company.strip().upper() for company in user_input.split(',')]
from_date = input("Enter the start date (YYYY-MM-DD): ")
to_date = input("Enter the end date (YYYY-MM-DD): ")

# Analyzing sentiment for each company
for company in companies:
    news_data = get_news_articles(api_key, company, from_date, to_date)
    
    if news_data and news_data.get('status') == 'ok':
        articles = news_data.get('articles', [])
        sentiment_scores = analyze_sentiment(articles)
        total_articles = len(articles)
        
        print(f"\nSentiment Analysis for {company} from {from_date} to {to_date}")
        print(f"Total articles analyzed: {total_articles}")
        print(f"Positive sentiment: {sentiment_scores['positive']} ({(sentiment_scores['positive']/total_articles)*100:.2f}%)")
        print(f"Neutral sentiment: {sentiment_scores['neutral']} ({(sentiment_scores['neutral']/total_articles)*100:.2f}%)")
        print(f"Negative sentiment: {sentiment_scores['negative']} ({(sentiment_scores['negative']/total_articles)*100:.2f}%)")
    else:
        print(f"No news articles found for {company} or failed to fetch the news data.")
