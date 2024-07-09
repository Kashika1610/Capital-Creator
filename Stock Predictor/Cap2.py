import yfinance as yf
import pandas as pd

# Function to fetch real-time prices and market cap for each stock
def get_real_time_data(stocks):
    data = []
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            hist = ticker.history(period='1d')
            market_cap = ticker.info.get('marketCap', None)
            price = hist['Close'].iloc[0] if not hist.empty else None
            data.append({'stock': stock, 'price': price, 'market_cap': market_cap})
        except Exception as e:
            print(f"Error fetching data for {stock}: {e}")
            data.append({'stock': stock, 'price': None, 'market_cap': None})
    return pd.DataFrame(data)

# Function to fetch stock information based on user input
def fetch_stock_info(stock):
    try:
        ticker = yf.Ticker(stock)
        info = ticker.info
        market_cap_category = pd.cut([info['marketCap']], bins=market_cap_bins, labels=market_cap_labels)[0]
        return {'stock': stock, 'price': info['previousClose'], 'market_cap': info['marketCap'], 'market_cap_category': market_cap_category}
    except Exception as e:
        return f"Error fetching data for {stock}: {e}"

# User input for stock ticker symbols
user_input = input("Enter stock ticker symbols separated by commas (e.g., AAPL, MSFT, GOOGL): ")
stocks = [stock.strip().upper() for stock in user_input.split(',')]

# Get the real-time data
df = get_real_time_data(stocks)

# Define the ranges for categorization based on price
price_bins = [0, 200, 1000, float('inf')]  # Adjust these ranges as needed
price_labels = ['Low', 'Medium', 'High']

# Categorize the companies into ranges based on their price
df['price_category'] = pd.cut(df['price'], bins=price_bins, labels=price_labels)

# Define the ranges for categorization based on market cap
market_cap_bins = [0, 2e9, 10e9, float('inf')]  # Adjust these ranges as needed
market_cap_labels = ['Small Cap', 'Mid Cap', 'Large Cap']

# Categorize the companies into ranges based on their market cap
df['market_cap_category'] = pd.cut(df['market_cap'], bins=market_cap_bins, labels=market_cap_labels)

# User input for a single stock ticker to fetch detailed information
user_stock = input("Enter a stock ticker symbol to fetch detailed information: ").upper()
stock_info = fetch_stock_info(user_stock)

# Display stock information
if isinstance(stock_info, dict):
    print(f"\nStock: {stock_info['stock']}")
    print(f"Price: ${stock_info['price']:.2f}")
    print(f"Market Cap: ${stock_info['market_cap']:,}")
    print(f"Category: {stock_info['market_cap_category']}")
else:
    print(stock_info)

# Display the DataFrame
print("\nReal-Time Data for Provided Stocks:")
print(df)


