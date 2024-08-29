import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

# Function to fetch real-time prices for stocks
def get_real_time_prices(stocks):
    prices = {}
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock.strip())
            todays_data = ticker.history(period='1d')
            if not todays_data.empty:
                prices[stock] = todays_data['Close'][0]
            else:
                prices[stock] = None
        except Exception as e:
            prices[stock] = None
            print(f"Error fetching price for {stock}: {e}")
    return prices

# Function to plot sentiment analysis results
def plot_sentiment(company, sentiment_scores):
    labels = ['Positive', 'Neutral', 'Negative']
    sizes = [sentiment_scores['positive'], sentiment_scores['neutral'], sentiment_scores['negative']]
    colors = ['#2E8B57', '#4682B4', '#CD5C5C']
    
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='#87CEFA')  # Light blue background
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax.set_title(f"Sentiment Analysis for {company}", color='black')
    
    return fig

# Function to plot stock price results
def plot_stock_prices(real_time_prices):
    stocks = list(real_time_prices.keys())
    prices = list(real_time_prices.values())
    
    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#87CEFA')  # Light blue background
    ax.bar(stocks, prices, color='#4682B4')
    ax.set_title("Real-Time Stock Prices", color='black')
    ax.set_ylabel("Price", color='black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    fig.tight_layout()
    
    return fig

# Function to run the sentiment analysis and stock price fetching
def run_analysis():
    api_key = "b11b4e7f8c7e4bb29fe4fbd19a24515e"  # Use your actual API key here
    companies = company_entry.get().split(',')
    
    # Calculate dates for the last two days
    to_date = datetime.today().strftime('%Y-%m-%d')
    from_date = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')

    if not api_key or not companies:
        messagebox.showerror("Error", "Please fill in all fields")
        return

    results_text.delete(1.0, tk.END)  # Clear previous results

    # Clear previous plots
    for widget in plots_frame.winfo_children():
        widget.destroy()

    # Run sentiment analysis and plot results
    for company in companies:
        news_data = get_news_articles(api_key, company.strip(), from_date, to_date)
        
        if news_data and news_data['status'] == 'ok':
            articles = news_data['articles']
            sentiment_scores = analyze_sentiment(articles)
            total_articles = len(articles)
            
            results_text.insert(tk.END, f"Sentiment Analysis for {company.strip()} from {from_date} to {to_date}\n")
            results_text.insert(tk.END, f"Total articles analyzed: {total_articles}\n")
            results_text.insert(tk.END, f"Positive sentiment: {sentiment_scores['positive']} ({(sentiment_scores['positive']/total_articles)*100:.2f}%)\n")
            results_text.insert(tk.END, f"Neutral sentiment: {sentiment_scores['neutral']} ({(sentiment_scores['neutral']/total_articles)*100:.2f}%)\n")
            results_text.insert(tk.END, f"Negative sentiment: {sentiment_scores['negative']} ({(sentiment_scores['negative']/total_articles)*100:.2f}%)\n")
            results_text.insert(tk.END, "\n")
            
            # Plot sentiment analysis results
            fig = plot_sentiment(company.strip(), sentiment_scores)
            canvas = FigureCanvasTkAgg(fig, master=plots_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)
        else:
            results_text.insert(tk.END, f"No news articles found for {company.strip()} or failed to fetch the news data.\n\n")
    
    # Fetch and plot real-time stock prices
    real_time_prices = get_real_time_prices(companies)
    data = {
        'stock': list(real_time_prices.keys()),
        'price': list(real_time_prices.values())
    }
    df = pd.DataFrame(data)
    
    # Define price ranges for categorization
    bins = [0, 200, 1000, float('inf')]  # Adjust these ranges as needed
    labels = ['Low', 'Medium', 'High']
    df['category'] = pd.cut(df['price'], bins=bins, labels=labels)

    results_text.insert(tk.END, "Real-Time Stock Prices and Categories:\n")
    for index, row in df.iterrows():
        price_str = f"{row['price']:.2f}" if row['price'] is not None else "N/A"
        results_text.insert(tk.END, f"Stock: {row['stock']} | Price: {price_str} | Category: {row['category']}\n")

    # Plot stock prices results
    fig = plot_stock_prices(real_time_prices)
    canvas = FigureCanvasTkAgg(fig, master=plots_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)

# Function to start the GUI in its own window
def start_gui():
    # Create the main window
    root = tk.Tk()
    root.title("News Sentiment Analysis & Stock Prices")
    root.geometry("1280x720")  # Set window size
    root.configure(bg='#87CEFA')  # Light blue background
    
    # Create a frame for the main content
    main_frame = tk.Frame(root, bg='#87CEFA')
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Create a canvas for the scrollable area
    canvas = tk.Canvas(main_frame, bg='#87CEFA')
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#87CEFA')

    scroll_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Configure the grid to expand with window size
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=0)

    # Create the input fields and labels
    ttk.Label(scrollable_frame, text="Companies (comma separated):", background='#87CEFA', foreground='black', font=("Arial", 12, "bold")).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
    global company_entry
    company_entry = ttk.Entry(scrollable_frame, width=60, font=("Arial", 12))
    company_entry.grid(row=0, column=1, padx=20, pady=10)

    # Create the run analysis button
    run_button = ttk.Button(scrollable_frame, text="Run Analysis", command=run_analysis)
    run_button.grid(row=1, column=0, columnspan=2, padx=20, pady=20)

    # Create the results display area
    global results_text
    results_text = scrolledtext.ScrolledText(scrollable_frame, wrap=tk.WORD, width=90, height=15, font=("Arial", 12), bg='#F0F8FF', foreground='black')
    results_text.grid(row=2, column=0, columnspan=2, padx=20, pady=10)

    # Create a frame for plots
    global plots_frame
    plots_frame = tk.Frame(scrollable_frame, bg='#87CEFA')
    plots_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

    # Update the scroll region
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)
    
    root.mainloop()

# Start the GUI
start_gui()