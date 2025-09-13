import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# Alpha Vantage API key (you need to get your own free key from https://www.alphavantage.co/support/#api-key)
API_KEY = '4LQORI5MVRWV0UNH'

def get_top_50_stocks():
    """Get top 50 US stocks by market cap"""
    top_50_stocks = [
        'MSFT', 'AMZN', 'META', 'NVO', 'LLY'
       # ,'AVGO', 'TSLA', 'QCOM', 'AMD', 'MU'
    ]
    return top_50_stocks

def fetch_alpha_vantage_data(symbol, interval='15min', output_size='compact'):
    """Fetch data from Alpha Vantage API"""
    # Map intervals to Alpha Vantage parameters
    interval_map = {
        '15min': '15min',
        '1h': '60min',
        '1d': 'daily'
    }
    
    function = 'TIME_SERIES_INTRADAY' if interval != '1d' else 'TIME_SERIES_DAILY'
    
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': function,
        'symbol': symbol,
        'interval': interval_map[interval],
        'outputsize': output_size,
        'apikey': API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if function == 'TIME_SERIES_DAILY':
            time_series_key = 'Time Series (Daily)'
        else:
            time_series_key = f'Time Series ({interval_map[interval]})'
        
        if time_series_key not in data:
            print(f"Error fetching {symbol}: {data.get('Note', 'Unknown error')}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
        df = df.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume'
        })
        
        # Convert columns to numeric
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            df[col] = pd.to_numeric(df[col])
        
        # Sort index in ascending order (oldest first)
        df = df.sort_index(ascending=True)
        
        return df
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_ema(data, period):
    """Calculate Exponential Moving Average"""
    return data.ewm(span=period, adjust=False).mean()

def calculate_bollinger_bands(data, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    sma = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    # Calculate Band Width (volatility indicator)
    band_width = (upper_band - lower_band) / sma
    
    # Calculate %B (position within bands)
    percent_b = (data - lower_band) / (upper_band - lower_band)
    
    return upper_band, sma, lower_band, band_width, percent_b

def calculate_atr(high, low, close, period=14):
    """Calculate Average True Range (ATR) for volatility measurement"""
    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Calculate ATR
    atr = tr.rolling(window=period).mean()
    return atr

def calculate_rsi(data, period=14):
    """Calculate RSI indicator"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def is_rsi_rising(rsi_series, lookback=3):
    """Check if RSI is rising over the specified lookback period"""
    if len(rsi_series) < lookback + 1:
        return False
    
    # Get recent RSI values
    recent_rsi = rsi_series.iloc[-lookback:]
    
    # Check if RSI is consistently rising
    rising = all(recent_rsi.iloc[i] > recent_rsi.iloc[i-1] for i in range(1, len(recent_rsi)))
    
    return rising

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
        spy_data = fetch_alpha_vantage_data('SPY', interval='1d', output_size='full')
        
        if spy_data is None or len(spy_data) < 200:
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
        # Get 15-minute data
        data_15m = fetch_alpha_vantage_data(ticker_symbol, interval='15min', output_size='compact')
        
        if data_15m is None or len(data_15m) < 100:
            return False, None, None, None, None, None, None, None, None, None
        
        # Calculate indicators
        data_15m['EMA20'] = calculate_ema(data_15m['Close'], 20)
        data_15m['EMA50'] = calculate_ema(data_15m['Close'], 50)
        data_15m['EMA200'] = calculate_ema(data_15m['Close'], 200)
        data_15m['Volume_MA20'] = data_15m['Volume'].rolling(window=20).mean()
        data_15m['RSI'] = calculate_rsi(data_15m['Close'], 14)
        
        # Calculate ADX
        data_15m['ADX'], _, _ = calculate_adx(data_15m['High'], data_15m['Low'], data_15m['Close'], 14)
        
        # Calculate ATR for volatility
        data_15m['ATR'] = calculate_atr(data_15m['High'], data_15m['Low'], data_15m['Close'], 14)
        data_15m['ATR_Pct'] = (data_15m['ATR'] / data_15m['Close']) * 100
        
        # Calculate Bollinger Bands
        (data_15m['BB_Upper'], data_15m['BB_Middle'], 
         data_15m['BB_Lower'], data_15m['BB_Width'], 
         data_15m['BB_PercentB']) = calculate_bollinger_bands(data_15m['Close'], 20, 2)
        
        # Calculate Stochastic
        k_line, d_line = calculate_stochastic(data_15m['High'], data_15m['Low'], data_15m['Close'])
        data_15m['Stoch_K'] = k_line
        data_15m['Stoch_D'] = d_line
        
        # Calculate Relative Strength
        relative_strength = calculate_relative_strength(data_15m, spy_data)
        
        # Get latest values
        latest = data_15m.iloc[-1]
        latest_rs = relative_strength.iloc[-1] if not relative_strength.empty else 0
        
        # Check RSI condition (RSI > 55 AND rising)
        rsi_above_55 = latest['RSI'] > 55 if pd.notna(latest['RSI']) else False
        rsi_rising = is_rsi_rising(data_15m['RSI'], lookback=3)
        rsi_condition = rsi_above_55 and rsi_rising
        
        # Check volatility condition (ATR < 2% of price)
        volatility_condition = latest['ATR_Pct'] < 2.0 if pd.notna(latest['ATR_Pct']) else False
        
        # Check Bollinger Band condition (Price above middle band and %B > 0.5)
        bb_condition = (latest['Close'] > latest['BB_Middle'] and 
                       latest['BB_PercentB'] > 0.5) if pd.notna(latest['BB_PercentB']) else False
        
        # Check other conditions
        price_ema_condition = (latest['Close'] > latest['EMA20'] > latest['EMA50'] > latest['EMA200'])
        volume_condition = latest['Volume'] > latest['Volume_MA20']
        adx_condition = latest['ADX'] > 25 if pd.notna(latest['ADX']) else False
        stoch_condition = check_stochastic_cross(data_15m['Stoch_K'], data_15m['Stoch_D'])
        
        conditions_met = (price_ema_condition and volume_condition and 
                         rsi_condition and adx_condition and stoch_condition and
                         volatility_condition and bb_condition)
        
        # Get previous RSI for trend display
        prev_rsi = data_15m['RSI'].iloc[-2] if len(data_15m['RSI']) > 1 else None
        rsi_trend = "↑" if rsi_rising else "↓" if prev_rsi and latest['RSI'] < prev_rsi else "→"
        
        return (conditions_met, latest_rs, latest['ADX'], latest['RSI'], 
                latest['Stoch_K'], latest['Stoch_D'], rsi_trend, latest['ATR_Pct'],
                latest['BB_PercentB'], latest['BB_Width'])
        
    except Exception as e:
        print(f"Error processing {ticker_symbol} for 15m: {e}")
        return False, None, None, None, None, None, None, None, None, None

def check_1h_conditions(ticker_symbol):
    """Check 1-hour timeframe conditions"""
    try:
        # Get 1-hour data
        data_1h = fetch_alpha_vantage_data(ticker_symbol, interval='1h', output_size='compact')
        
        if data_1h is None or len(data_1h) < 100:
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
    spy_data_15m = fetch_alpha_vantage_data('SPY', interval='15min', output_size='compact')
    if spy_data_15m is None:
        print("Error fetching SPY data for relative strength calculation")
        return []
    
    qualifying_stocks = []
    stock_details = []
    
    print("Analyzing stocks...")
    for i, ticker in enumerate(stocks, 1):
        print(f"Processing {ticker} ({i}/{len(stocks)})...")
        
        # Check both timeframe conditions
        (condition_15m, rel_strength, adx_value, rsi_value, 
         stoch_k, stoch_d, rsi_trend, atr_pct, 
         bb_percent, bb_width) = check_15m_conditions(ticker, spy_data_15m)
        condition_1h = check_1h_conditions(ticker)
        
        if condition_15m and condition_1h:
            qualifying_stocks.append(ticker)
            stock_details.append({
                'ticker': ticker,
                'relative_strength': rel_strength,
                'adx': adx_value,
                'rsi': rsi_value,
                'stoch_k': stoch_k,
                'stoch_d': stoch_d,
                'rsi_trend': rsi_trend,
                'atr_pct': atr_pct,
                'bb_percent': bb_percent,
                'bb_width': bb_width
            })
            print(f"✓ {ticker} qualifies! RS: {rel_strength:.3f}, ADX: {adx_value:.1f}, "
                  f"RSI: {rsi_value:.1f}{rsi_trend}, Stoch: K={stoch_k:.1f}/D={stoch_d:.1f}, "
                  f"ATR%: {atr_pct:.2f}%, %B: {bb_percent:.2f}, BB Width: {bb_width:.4f}")
        
        # Add delay to avoid rate limiting (Alpha Vantage has 5 requests per minute limit for free tier)
        time.sleep(12)  # 12 seconds delay to stay under 5 requests per minute
    
    # Sort by relative strength (descending)
    if stock_details:
        stock_details.sort(key=lambda x: x['relative_strength'], reverse=True)
        qualifying_stocks = [stock['ticker'] for stock in stock_details]
    
    return qualifying_stocks, stock_details

def main():
    """Main execution function"""
    print("Stock Screening Tool (Alpha Vantage API)")
    print("=" * 90)
    print("Filters:")
    print("- Market: SPY > EMA200 (Daily)")
    print("- 15m: Price > EMA20 > EMA50 > EMA200, Volume > 20MA")
    print("- 15m: RSI(14) > 55 AND Rising, ADX > 25")
    print("- 15m: Stochastic %K crosses above %D")
    print("- 15m: ATR% < 2.0 (Low Volatility Filter)")
    print("- 15m: Price > BB Middle Band AND %B > 0.5 (Bollinger Band Filter)")
    print("- 1h: EMA50 > EMA200")
    print("- Relative Strength Ratio (vs SPY)")
    print("=" * 90)
    
    start_time = datetime.now()
    results, details = analyze_stocks()
    
    print("\n" + "=" * 90)
    print("SCREENING RESULTS")
    print("=" * 90)
    
    if results:
        print(f"Qualifying stocks ({len(results)}):")
        print("\n{:<8} {:<8} {:<12} {:<8} {:<10} {:<12} {:<12} {:<10} {:<10} {:<10}".format(
            "Rank", "Ticker", "Rel Strength", "ADX", "RSI", "Stoch %K", "Stoch %D", "ATR %", "%B", "BB Width"
        ))
        print("-" * 90)
        
        for i, stock_info in enumerate(details, 1):
            print("{:<8} {:<8} {:<12.3f} {:<8.1f} {:<10} {:<12.1f} {:<12.1f} {:<10.2f} {:<10.2f} {:<10.4f}".format(
                f"#{i}", 
                stock_info['ticker'], 
                stock_info['relative_strength'],
                stock_info['adx'],
                f"{stock_info['rsi']:.1f}{stock_info['rsi_trend']}",
                stock_info['stoch_k'],
                stock_info['stoch_d'],
                stock_info['atr_pct'],
                stock_info['bb_percent'],
                stock_info['bb_width']
            ))
            
        print("\n💡 Key:")
        print("   RSI Trend: ↑ = Rising, ↓ = Falling, → = Flat")
        print("   Stochastic Cross: Bullish when %K crosses above %D")
        print("   ATR %: Lower values indicate lower volatility (<2% is good)")
        print("   %B: Position in Bollinger Bands (0-1, >0.5 = above middle)")
        print("   BB Width: Band width as % of price (higher = more volatility)")
        
    else:
        print("No stocks meet all the criteria.")
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\nAnalysis completed in {duration.total_seconds():.2f} seconds")

if __name__ == "__main__":
    main()