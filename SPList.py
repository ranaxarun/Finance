import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

def get_top_50_stocks():
    """Get top 50 US stocks by market cap"""
    top_50_stocks = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'JNJ',
        'XOM', 'V', 'JPM', 'WMT', 'PG', 'MA', 'CVX', 'HD', 'LLY', 'ABBV',
        'AVGO', 'PEP', 'KO', 'MRK', 'BAC', 'PFE', 'TMO', 'COST', 'DIS', 'CSCO',
        'DHR', 'VZ', 'ADBE', 'ABT', 'ACN', 'CMCSA', 'NFLX', 'WFC', 'CRM', 'NKE',
        'PM', 'LIN', 'RTX', 'T', 'HON', 'QCOM', 'AMD', 'INTU', 'AMGN', 'IBM',
        'ASML', 'NVO', 'MU', 'PLTR', 'RDDT','BABA','UBER','DASH'

    ]
    return top_50_stocks

def calculate_ema(data, period):
    """Calculate Exponential Moving Average"""
    return data.ewm(span=period, adjust=False).mean()

def calculate_rsi(data, period=14):
    """Calculate RSI indicator"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_stochastic(high, low, close, k_period=14, d_period=3):
    """Calculate Stochastic Oscillator"""
    # Calculate %K line
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    
    k_line = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    
    # Calculate %D line (signal line) - SMA of %K
    d_line = k_line.rolling(window=d_period).mean()
    
    return k_line, d_line

def check_stochastic_cross(k_line, d_line):
    """Check if %K line crosses above %D line"""
    if len(k_line) < 2 or len(d_line) < 2:
        return False
    
    # Check if current %K > %D and previous %K <= %D
    current_k = k_line.iloc[-1]
    current_d = d_line.iloc[-1]
    prev_k = k_line.iloc[-2]
    prev_d = d_line.iloc[-2]
    
    return (current_k > current_d) and (prev_k <= prev_d)

def calculate_adx(high, low, close, period=14):
    """Calculate Average Directional Index (ADX)"""
    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Calculate Directional Movement
    up_move = high - high.shift()
    down_move = low.shift() - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    
    # Calculate smoothed values
    tr_smooth = tr.rolling(window=period).mean()
    plus_dm_smooth = pd.Series(plus_dm, index=high.index).rolling(window=period).mean()
    minus_dm_smooth = pd.Series(minus_dm, index=high.index).rolling(window=period).mean()
    
    # Calculate Directional Indicators
    plus_di = 100 * (plus_dm_smooth / tr_smooth)
    minus_di = 100 * (minus_dm_smooth / tr_smooth)
    
    # Calculate DX and ADX
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
    adx = dx.rolling(window=period).mean()
    
    return adx, plus_di, minus_di

def calculate_relative_strength(stock_data, spy_data):
    """Calculate Relative Strength Ratio (Stock vs SPY)"""
    stock_returns = stock_data['Close'].pct_change()
    spy_returns = spy_data['Close'].pct_change()
    
    # Calculate relative strength (stock performance vs SPY)
    relative_strength = (1 + stock_returns) / (1 + spy_returns)
    relative_strength = relative_strength.cumprod()
    
    return relative_strength

def check_spy_above_ema200():
    """Check if SPY is above its 200-EMA on daily timeframe"""
    try:
        spy = yf.Ticker('SPY')
        spy_data = spy.history(period='300d', interval='1d')
        
        if len(spy_data) < 200:
            return False
        
        spy_data['EMA200'] = calculate_ema(spy_data['Close'], 200)
        latest = spy_data.iloc[-1]
        
        return latest['Close'] > latest['EMA200']
        
    except Exception as e:
        print(f"Error checking SPY condition: {e}")
        return False

def check_15m_conditions(ticker_symbol, spy_data):
    """Check 15-minute timeframe conditions"""
    try:
        # Get 15-minute data for the last 30 days
        stock = yf.Ticker(ticker_symbol)
        data_15m = stock.history(period='30d', interval='15m')
        
        if len(data_15m) < 100:
            return False, None, None, None, None, None
        
        # Calculate indicators
        data_15m['EMA20'] = calculate_ema(data_15m['Close'], 20)
        data_15m['EMA50'] = calculate_ema(data_15m['Close'], 50)
        data_15m['EMA200'] = calculate_ema(data_15m['Close'], 200)
        data_15m['Volume_MA20'] = data_15m['Volume'].rolling(window=20).mean()
        data_15m['RSI'] = calculate_rsi(data_15m['Close'], 14)
        
        # Calculate ADX
        data_15m['ADX'], _, _ = calculate_adx(data_15m['High'], data_15m['Low'], data_15m['Close'], 14)
        
        # Calculate Stochastic
        k_line, d_line = calculate_stochastic(data_15m['High'], data_15m['Low'], data_15m['Close'])
        data_15m['Stoch_K'] = k_line
        data_15m['Stoch_D'] = d_line
        
        # Calculate Relative Strength
        relative_strength = calculate_relative_strength(data_15m, spy_data)
        
        # Get latest values
        latest = data_15m.iloc[-1]
        latest_rs = relative_strength.iloc[-1] if not relative_strength.empty else 0
        
        # Check conditions
        price_ema_condition = (latest['Close'] > latest['EMA20'] > latest['EMA50'] > latest['EMA200'])
        volume_condition = latest['Volume'] > latest['Volume_MA20']
        rsi_condition = latest['RSI'] > 55 if pd.notna(latest['RSI']) else False
        adx_condition = latest['ADX'] > 25 if pd.notna(latest['ADX']) else False
        stoch_condition = check_stochastic_cross(data_15m['Stoch_K'], data_15m['Stoch_D'])
        
        conditions_met = (price_ema_condition and volume_condition and 
                         rsi_condition and adx_condition and stoch_condition)
        
        return (conditions_met, latest_rs, latest['ADX'], latest['RSI'], 
                latest['Stoch_K'], latest['Stoch_D'])
        
    except Exception as e:
        print(f"Error processing {ticker_symbol} for 15m: {e}")
        return False, None, None, None, None, None

def check_1h_conditions(ticker_symbol):
    """Check 1-hour timeframe conditions"""
    try:
        # Get 1-hour data for the last 60 days
        stock = yf.Ticker(ticker_symbol)
        data_1h = stock.history(period='60d', interval='1h')
        
        if len(data_1h) < 100:
            return False
        
        # Calculate indicators
        data_1h['EMA50'] = calculate_ema(data_1h['Close'], 50)
        data_1h['EMA200'] = calculate_ema(data_1h['Close'], 200)
        
        # Get latest values
        latest = data_1h.iloc[-1]
        
        # Check condition
        return latest['EMA50'] > latest['EMA200']
        
    except Exception as e:
        print(f"Error processing {ticker_symbol} for 1h: {e}")
        return False

def analyze_stocks():
    """Main function to analyze stocks"""
    print("Fetching top 50 stocks...")
    stocks = get_top_50_stocks()
    
    print("Checking SPY condition...")
    spy_condition = check_spy_above_ema200()
    if not spy_condition:
        print("❌ SPY is not above its 200-EMA. Market condition not favorable.")
        return []
    
    print("✓ SPY is above its 200-EMA. Proceeding with analysis...")
    
    # Get SPY data for relative strength calculation
    spy = yf.Ticker('SPY')
    spy_data_15m = spy.history(period='30d', interval='15m')
    
    qualifying_stocks = []
    stock_details = []
    
    print("Analyzing stocks...")
    for i, ticker in enumerate(stocks, 1):
        print(f"Processing {ticker} ({i}/{len(stocks)})...")
        
        # Check both timeframe conditions
        (condition_15m, rel_strength, adx_value, rsi_value, 
         stoch_k, stoch_d) = check_15m_conditions(ticker, spy_data_15m)
        condition_1h = check_1h_conditions(ticker)
        
        if condition_15m and condition_1h:
            qualifying_stocks.append(ticker)
            stock_details.append({
                'ticker': ticker,
                'relative_strength': rel_strength,
                'adx': adx_value,
                'rsi': rsi_value,
                'stoch_k': stoch_k,
                'stoch_d': stoch_d
            })
            print(f"✓ {ticker} qualifies! RS: {rel_strength:.3f}, ADX: {adx_value:.1f}, "
                  f"RSI: {rsi_value:.1f}, Stoch: K={stoch_k:.1f}/D={stoch_d:.1f}")
        
        # Add delay to avoid rate limiting
        time.sleep(0.5)
    
    # Sort by relative strength (descending)
    if stock_details:
        stock_details.sort(key=lambda x: x['relative_strength'], reverse=True)
        qualifying_stocks = [stock['ticker'] for stock in stock_details]
    
    return qualifying_stocks, stock_details

def main():
    """Main execution function"""
    print("Stock Screening Tool")
    print("=" * 70)
    print("Filters:")
    print("- Market: SPY > EMA200 (Daily)")
    print("- 15m: Price > EMA20 > EMA50 > EMA200, Volume > 20MA, RSI(14) > 55, ADX > 25")
    print("- 15m: Stochastic %K crosses above %D")
    print("- 1h: EMA50 > EMA200")
    print("- Relative Strength Ratio (vs SPY)")
    print("=" * 70)
    
    start_time = datetime.now()
    results, details = analyze_stocks()
    
    print("\n" + "=" * 70)
    print("SCREENING RESULTS")
    print("=" * 70)
    
    if results:
        print(f"Qualifying stocks ({len(results)}):")
        print("\n{:<8} {:<8} {:<12} {:<8} {:<8} {:<12} {:<12}".format(
            "Rank", "Ticker", "Rel Strength", "ADX", "RSI", "Stoch %K", "Stoch %D"
        ))
        print("-" * 70)
        
        for i, stock_info in enumerate(details, 1):
            print("{:<8} {:<8} {:<12.3f} {:<8.1f} {:<8.1f} {:<12.1f} {:<12.1f}".format(
                f"#{i}", 
                stock_info['ticker'], 
                stock_info['relative_strength'],
                stock_info['adx'],
                stock_info['rsi'],
                stock_info['stoch_k'],
                stock_info['stoch_d']
            ))
            
        print("\n💡 Stochastic Cross: Bullish signal when %K (blue) crosses above %D (red)")
        
    else:
        print("No stocks meet all the criteria.")
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\nAnalysis completed in {duration.total_seconds():.2f} seconds")

if __name__ == "__main__":
    main()