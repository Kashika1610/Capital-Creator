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
        return response.json()
    else:
        print(f"Failed to fetch news articles for {query}: {response.status_code} - {response.text}")
        return None

# Function to analyze sentiment of the news articles
def analyze_sentiment(articles):
    sentiment_scores = {'positive': 0, 'neutral': 0, 'negative': 0}
    for article in articles:
        title = article['title'] if article['title'] else ""
        description = article['description'] if article['description'] else ""
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

# List of companies
companies = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',  # Big cap examples
    'ZM', 'SNAP', 'DOCU', 'FSLY',  # Mid cap examples
    'PLTR', 'NET', 'CRWD', 'NIO'   # Other examples
]

# Parameters for fetching news articles
from_date = '2024-06-30'
to_date = '2024-06-30'

# Analyzing sentiment for each company
for company in companies:
    news_data = get_news_articles(api_key, company, from_date, to_date)
    
    if news_data and news_data['status'] == 'ok':
        articles = news_data['articles']
        sentiment_scores = analyze_sentiment(articles)
        total_articles = len(articles)
        
        print(f"Sentiment Analysis for {company} from {from_date} to {to_date}")
        print(f"Total articles analyzed: {total_articles}")
        print(f"Positive sentiment: {sentiment_scores['positive']} ({(sentiment_scores['positive']/total_articles)*100:.2f}%)")
        print(f"Neutral sentiment: {sentiment_scores['neutral']} ({(sentiment_scores['neutral']/total_articles)*100:.2f}%)")
        print(f"Negative sentiment: {sentiment_scores['negative']} ({(sentiment_scores['negative']/total_articles)*100:.2f}%)")
        print()
    else:
        print(f"No news articles found for {company} or failed to fetch the news data.")
