import yfinance as yf
import pandas as pd

# List of stock ticker symbols
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',  # Big cap examples
    'ZM', 'SNAP', 'DOCU', 'FSLY',  # Mid cap examples
    'PLTR', 'NET', 'CRWD', 'NIO'   ]

# Fetch real-time prices for each stock
def get_real_time_prices(stocks):
    prices = {}
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            prices[stock] = ticker.history(period='1d')['Close'][0]
        except Exception as e:
            prices[stock] = None
            print(f"Error fetching price for {stock}: {e}")
    return prices

# Get the real-time prices
real_time_prices = get_real_time_prices(stocks)

# Create a DataFrame with the stock ticker symbols and their real-time prices
data = {
    'stock': list(real_time_prices.keys()),
    'price': list(real_time_prices.values())
}
df = pd.DataFrame(data)

# Define the ranges for categorization
bins = [0, 200, 1000, float('inf')]  # Adjust these ranges as needed
labels = ['Low', 'Medium', 'High']

# Categorize the companies into ranges based on their price
df['category'] = pd.cut(df['price'], bins=bins, labels=labels)

# Function to fetch stock information
def fetch_stock_info(stock):
    try:
        info = yf.Ticker(stock).info
        return info
    except Exception as e:
        return f"Error fetching data for {stock}: {e}"

# Fetch stock information for each category
categories = df['category'].unique()

for category in categories:
    print(f"\nCategory: {category}")
    for stock in df[df['category'] == category]['stock']:
        info = fetch_stock_info(stock)
        print(f"Information for {stock}: {info}")

# Print the categorized DataFrame
print("\nCategorized DataFrame:")
print(df)