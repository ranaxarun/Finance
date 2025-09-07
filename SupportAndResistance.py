import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.signal import argrelextrema

# Configuration
TICKERS = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'JNJ',
        'XOM', 'V', 'JPM', 'WMT', 'PG', 'MA', 'CVX', 'HD', 'LLY', 'ABBV',
        'AVGO', 'PEP', 'KO', 'MRK', 'BAC', 'PFE', 'TMO', 'COST', 'DIS', 'CSCO',
        'DHR', 'VZ', 'ADBE', 'ABT', 'ACN', 'CMCSA', 'NFLX', 'WFC', 'CRM', 'NKE',
        'PM', 'LIN', 'RTX', 'T', 'HON', 'QCOM', 'AMD', 'INTU', 'AMGN', 'IBM',
        'ASML', 'NVO', 'MU', 'PLTR', 'RDDT','BABA','UBER','DASH'

    
    ]
PERIOD = "YTD"
INTERVAL = "1d"
MIN_DISTANCE = 5  # Minimum distance between swing points
WINDOW_SIZE = 20  # Window for local maxima/minima detection
SUPPORT_RESISTANCE_TOLERANCE = 0.02  # 2% tolerance for level clustering

def get_stock_data(ticker, period, interval):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if df.empty:
            print(f"No data found for {ticker}")
            return None
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def find_local_extrema(df, window_size=20):
    """Find local maxima and minima in price data"""
    # Find local maxima (resistance points)
    local_maxima = argrelextrema(df['High'].values, np.greater, order=window_size)[0]
    resistance_points = df.iloc[local_maxima]['High']
    
    # Find local minima (support points)
    local_minima = argrelextrema(df['Low'].values, np.less, order=window_size)[0]
    support_points = df.iloc[local_minima]['Low']
    
    return support_points, resistance_points

def cluster_levels(price_points, tolerance_percent=0.02):
    """Cluster nearby price points into significant levels"""
    if len(price_points) == 0:
        return []
    
    # Sort price points
    sorted_prices = sorted(price_points)
    
    clusters = []
    current_cluster = [sorted_prices[0]]
    
    for price in sorted_prices[1:]:
        # Check if price is within tolerance of current cluster
        if abs(price - np.mean(current_cluster)) / np.mean(current_cluster) <= tolerance_percent:
            current_cluster.append(price)
        else:
            # Save current cluster and start new one
            clusters.append(current_cluster)
            current_cluster = [price]
    
    clusters.append(current_cluster)
    
    # Return the mean price for each cluster
    return [np.mean(cluster) for cluster in clusters]

def filter_major_levels(levels, price_data, min_touches=3):
    """Filter levels based on number of price touches"""
    major_levels = []
    
    for level in levels:
        touches = 0
        
        # Count how many times price approached this level
        for i, (high, low) in enumerate(zip(price_data['High'], price_data['Low'])):
            # Check if price came close to this level (within 1%)
            if abs(high - level) / level <= 0.01 or abs(low - level) / level <= 0.01:
                touches += 1
        
        if touches >= min_touches:
            major_levels.append((level, touches))
    
    return sorted(major_levels, key=lambda x: x[0])

def identify_support_resistance(df):
    """Identify major support and resistance levels"""
    # Find local extrema
    support_points, resistance_points = find_local_extrema(df, WINDOW_SIZE)
    
    # Cluster nearby points into levels
    support_levels = cluster_levels(support_points, SUPPORT_RESISTANCE_TOLERANCE)
    resistance_levels = cluster_levels(resistance_points, SUPPORT_RESISTANCE_TOLERANCE)
    
    # Filter for major levels with multiple touches
    major_support = filter_major_levels(support_levels, df)
    major_resistance = filter_major_levels(resistance_levels, df)
    
    return major_support, major_resistance

def plot_levels(ticker, df, support_levels, resistance_levels):
    """Plot stock price with support and resistance levels"""
    plt.figure(figsize=(12, 8))
    
    # Plot price data
    plt.plot(df.index, df['Close'], label='Close Price', linewidth=1, alpha=0.7)
    plt.fill_between(df.index, df['Low'], df['High'], alpha=0.2, label='Daily Range')
    
    # Plot support levels
    for level, touches in support_levels:
        plt.axhline(y=level, color='green', linestyle='--', alpha=0.7, 
                   label=f'Support ${level:.2f} ({touches} touches)' if level == support_levels[0][0] else "")
        plt.text(df.index[-1], level, f' S: ${level:.2f}', verticalalignment='center')
    
    # Plot resistance levels
    for level, touches in resistance_levels:
        plt.axhline(y=level, color='red', linestyle='--', alpha=0.7,
                   label=f'Resistance ${level:.2f} ({touches} touches)' if level == resistance_levels[0][0] else "")
        plt.text(df.index[-1], level, f' R: ${level:.2f}', verticalalignment='center')
    
    plt.title(f'{ticker} - Major Support & Resistance Levels (Last 6 Months)')
    plt.xlabel('Date')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def analyze_stock(ticker):
    """Complete analysis for a single stock"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {ticker}")
    print(f"{'='*60}")
    
    # Get data
    df = get_stock_data(ticker, PERIOD, INTERVAL)
    if df is None or len(df) < 30:
        print(f"Insufficient data for {ticker}")
        return
    
    # Identify levels
    support_levels, resistance_levels = identify_support_resistance(df)
    
    # Print results
    print(f"\nMajor Support Levels for {ticker}:")
    for level, touches in support_levels:
        print(f"  ${level:.2f} - {touches} price touches")
    
    print(f"\nMajor Resistance Levels for {ticker}:")
    for level, touches in resistance_levels:
        print(f"  ${level:.2f} - {touches} price touches")
    
    # Current price analysis
    current_price = df['Close'].iloc[-1]
    print(f"\nCurrent Price: ${current_price:.2f}")
    
    # Find nearest support and resistance
    nearest_support = max([level for level, _ in support_levels if level < current_price], default=None)
    nearest_resistance = min([level for level, _ in resistance_levels if level > current_price], default=None)
    
    if nearest_support:
        support_distance = ((current_price - nearest_support) / current_price) * 100
        print(f"Nearest Support: ${nearest_support:.2f} ({support_distance:.2f}% below)")
    
    if nearest_resistance:
        resistance_distance = ((nearest_resistance - current_price) / current_price) * 100
        print(f"Nearest Resistance: ${nearest_resistance:.2f} ({resistance_distance:.2f}% above)")
    
    # Plot if there are significant levels
   # if support_levels or resistance_levels:
   #     plot_levels(ticker, df, support_levels, resistance_levels)
   # else:
   #     print("No significant support/resistance levels found.")

def main():
    """Main function to analyze all stocks"""
    print("Analyzing Major Support & Resistance Levels for Top US Stocks")
    print("Timeframe: Last 6 months, Daily data")
    print(f"Stocks: {', '.join(TICKERS)}")
    print(f"{'='*60}")
    
    results = {}
    
    for ticker in TICKERS:
        try:
            analyze_stock(ticker)
            results[ticker] = "Analysis completed"
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            results[ticker] = f"Error: {e}"
    
    print(f"\n{'='*60}")
    print("Analysis Summary:")
    for ticker, status in results.items():
        print(f"{ticker}: {status}")

if __name__ == "__main__":
    main()