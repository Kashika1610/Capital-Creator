import tkinter as tk
from tkinter import scrolledtext
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# List of stock ticker symbols
stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'ZM', 'SNAP', 'DOCU', 'FSLY', 'PLTR', 'NET', 'CRWD', 'NIO']

# Function to fetch real-time prices for each stock
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

# Function to categorize stocks and display the DataFrame
def categorize_stocks():
    real_time_prices = get_real_time_prices(stocks)
    
    # Create a DataFrame with the stock ticker symbols and their real-time prices
    data = {'stock': list(real_time_prices.keys()), 'price': list(real_time_prices.values())}
    df = pd.DataFrame(data)
    
    # Define the ranges for categorization
    bins = [0, 200, 1000, float('inf')]
    labels = ['Low', 'Medium', 'High']
    
    # Categorize the companies into ranges based on their price
    df['category'] = pd.cut(df['price'], bins=bins, labels=labels)
    
    # Display the categorized DataFrame in the GUI
    result_text.delete(1.0, tk.END)
    
    # Formatting output to space out companies and prices
    result_text.insert(tk.END, "Stock\tPrice\tCategory\n")
    result_text.insert(tk.END, "-" * 30 + "\n")
    for index, row in df.iterrows():
        result_text.insert(tk.END, f"{row['stock']:<8}{row['price']:>10.2f}   {row['category']}\n")
    
    # Plotting the categorized stock prices
    plot_graph(df)

# Function to plot the stock prices graph
def plot_graph(df):
    fig, ax = plt.subplots()
    categories = df['category'].unique()
    
    for category in categories:
        cat_data = df[df['category'] == category]
        ax.bar(cat_data['stock'], cat_data['price'], label=f"{category} Price")
    
    ax.set_title('Stock Prices by Category')
    ax.set_ylabel('Price ($)')
    ax.set_xlabel('Stock')
    ax.legend()
    
    # Embedding the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=frame_graph)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# GUI Setup
root = tk.Tk()
root.title("Stock Price Categorization & Info")
root.geometry("1920x1080")
root.configure(bg='navy')
# Frame for graph display
frame_graph = tk.Frame(root, bg='black')
frame_graph.place(relx=0.5, rely=0.6, anchor=tk.CENTER, relwidth=0.9, relheight=0.4)
# Text box for displaying results with increased size
result_text = scrolledtext.ScrolledText(root, height=15, width=100, bg='white', fg='black', font=("Arial", 14))
result_text.pack(pady=20)
# Automatically categorize stocks and display output on startup
categorize_stocks()
# Start the GUI event loop
root.mainloop()