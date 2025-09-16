import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

def get_sp500_stocks():
    """Get all S&P 500 stocks"""
    sp500_stocks = [
        'MMM', 'AOS', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMD', 'AES', 'AFL', 'A', 
        'APD', 'AKAM', 'ALK', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 
        'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 
        'AWK', 'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'ADI', 'ANSS', 'AON', 'APA', 
        'AAPL', 'AMAT', 'APTV', 'ACGL', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 
        'ADP', 'AZO', 'AVB', 'AVY', 'AXON', 'BKR', 'BALL', 'BAC', 'BBWI', 'BAX', 
        'BDX', 'WRB', 'BRK-B', 'BBY', 'BIO', 'TECH', 'BIIB', 'BLK', 'BK', 'BA', 
        'BKNG', 'BWA', 'BXP', 'BSX', 'BMY', 'AVGO', 'BR', 'BRO', 'BF-B', 'CHRW', 
        'CDNS', 'CZR', 'CPT', 'CPB', 'COF', 'CAH', 'KMX', 'CCL', 'CARR', 'CTLT', 
        'CAT', 'CBOE', 'CBRE', 'CDW', 'CE', 'CNC', 'CNP', 'CDAY', 'CF', 'CRL', 
        'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'CINF', 'CTAS', 'CSCO', 
        'C', 'CFG', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'CL', 'CMCSA', 'CMA', 
        'CAG', 'COP', 'ED', 'STZ', 'CEG', 'COO', 'CPRT', 'GLW', 'CTVA', 'CSGP', 
        'COST', 'CTRA', 'CCI', 'CSX', 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 
        'DE', 'DAL', 'XRAY', 'DVN', 'DXCM', 'FANG', 'DLR', 'DFS', 'DIS', 'DG', 
        'DLTR', 'D', 'DPZ', 'DOV', 'DOW', 'DTE', 'DUK', 'DD', 'DXC', 'EMN', 
        'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'ELV', 'LLY', 'EMR', 'ENPH', 
        'ETR', 'EOG', 'EPAM', 'EQT', 'EFX', 'EQIX', 'EQR', 'ESS', 'EL', 'ETYS', 
        'EG', 'EVRG', 'ES', 'EXC', 'EXPE', 'EXPD', 'EXR', 'XOM', 'FFIV', 'FDS', 
        'FICO', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FSLR', 'FE', 'FISV', 'FLT', 
        'FMC', 'F', 'FTNT', 'FTV', 'FOXA', 'FOX', 'BEN', 'FCX', 'GRMN', 'IT', 
        'GE', 'GNRC', 'GD', 'GIS', 'GM', 'GPC', 'GILD', 'GL', 'GPN', 'GS', 
        'HAL', 'HIG', 'HAS', 'HCA', 'PEAK', 'HSIC', 'HSY', 'HES', 'HPE', 'HLT', 
        'HOLX', 'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUM', 'HBAN', 'HII', 
        'IBM', 'IEX', 'IDXX', 'ITW', 'ILMN', 'INCY', 'IR', 'PODD', 'INTC', 'ICE', 
        'IFF', 'IP', 'IPG', 'INTU', 'ISRG', 'IVZ', 'INVH', 'IQV', 'IRM', 'JBHT', 
        'JBL', 'JKHY', 'J', 'JNJ', 'JCI', 'JPM', 'JNPR', 'K', 'KDP', 'KEY', 
        'KEYS', 'KMB', 'KIM', 'KMI', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 
        'LW', 'LVS', 'LDOS', 'LEN', 'LNC', 'LIN', 'LYV', 'LKQ', 'LMT', 'L', 
        'LOW', 'LULU', 'LYB', 'MTB', 'MRO', 'MPC', 'MKTX', 'MAR', 'MMC', 'MLM', 
        'MAS', 'MA', 'MTCH', 'MKC', 'MCD', 'MCK', 'MDT', 'MRK', 'META', 'MET', 
        'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MRNA', 'MHK', 'MOH', 'TAP', 
        'MDLZ', 'MPWR', 'MNST', 'MCO', 'MS', 'MOS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 
        'NFLX', 'NWL', 'NEM', 'NWSA', 'NWS', 'NEE', 'NKE', 'NI', 'NDSN', 'NSC', 
        'NTRS', 'NOC', 'NCLH', 'NRG', 'NUE', 'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 
        'ODFL', 'OMC', 'ON', 'OKE', 'ORCL', 'OTIS', 'PCAR', 'PKG', 'PARA', 'PH', 
        'PAYX', 'PAYC', 'PYPL', 'PNR', 'PEP', 'PFE', 'PCG', 'PM', 'PSX', 'PNW', 
        'PXD', 'PNC', 'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 
        'PEG', 'PTC', 'PSA', 'PHM', 'QRVO', 'PWR', 'QCOM', 'DGX', 'RL', 'RJF', 
        'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RVTY', 'RHI', 'ROK', 
        'ROL', 'ROP', 'ROST', 'RCL', 'SPGI', 'CRM', 'SBAC', 'SLB', 'STX', 'SEE', 
        'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SJM', 'SNA', 'SEDG', 'SO', 'LUV', 
        'SWK', 'SBUX', 'STT', 'STLD', 'STE', 'SYK', 'SYF', 'SNPS', 'SYY', 'TMUS', 
        'TROW', 'TTWO', 'TPR', 'TRGP', 'TGT', 'TEL', 'TDY', 'TFX', 'TER', 'TSLA', 
        'TXN', 'TXT', 'TMO', 'TJX', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB', 'TFC', 
        'TYL', 'TSN', 'USB', 'UDR', 'ULTA', 'UNP', 'UAL', 'UNH', 'UPS', 'URI', 
        'UHS', 'VLO', 'VTR', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VFC', 'VTRS', 'VICI', 
        'V', 'VMC', 'WAB', 'WBA', 'WMT', 'WBD', 'WM', 'WAT', 'WEC', 'WFC', 
        'WELL', 'WST', 'WDC', 'WRK', 'WY', 'WHR', 'WMB', 'WTW', 'GWW', 'WYNN', 
        'XEL', 'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZION', 'ZTS'
    ]
    return sp500_stocks

def calculate_ema(data, period):
    """Calculate Exponential Moving Average"""
    return data.ewm(span=period, adjust=False).mean()

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

def is_indicator_rising(indicator_series, lookback=3):
    """Check if an indicator is rising over the specified lookback period"""
    if len(indicator_series) < lookback + 1:
        return False
    
    # Get recent indicator values
    recent_values = indicator_series.iloc[-lookback:]
    
    # Check if indicator is consistently rising
    rising = all(recent_values.iloc[i] > recent_values.iloc[i-1] for i in range(1, len(recent_values)))
    
    return rising

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

def check_daily_conditions(ticker_symbol, spy_data):
    """Check daily timeframe conditions for individual stock"""
    try:
        # Get daily data
        stock = yf.Ticker(ticker_symbol)
        data_daily = stock.history(period='300d', interval='1d')
        
        if len(data_daily) < 200:
            return False, 0, 0
        
        # Calculate EMAs
        data_daily['EMA50'] = calculate_ema(data_daily['Close'], 50)
        data_daily['EMA200'] = calculate_ema(data_daily['Close'], 200)
        
        # Calculate relative strength
        relative_strength = calculate_relative_strength(data_daily, spy_data)
        
        # Get latest values
        latest = data_daily.iloc[-1]
        latest_rs = relative_strength.iloc[-1] if not relative_strength.empty else 0
        current_price = latest['Close']
        
        # Check conditions
        ema_condition = latest['EMA50'] > latest['EMA200']
        rs_condition = latest_rs > 1
        
        return (ema_condition and rs_condition), latest_rs, current_price
        
    except Exception as e:
        print(f"Error processing {ticker_symbol} for daily: {e}")
        return False, 0, 0

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

def check_15m_conditions(ticker_symbol):
    """Check 15-minute timeframe conditions"""
    try:
        # Get 15-minute data for the last 30 days
        stock = yf.Ticker(ticker_symbol)
        data_15m = stock.history(period='30d', interval='15m')
        
        if len(data_15m) < 100:
            return False, None, None, None, None, None, None, None
        
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
        
        # Get latest values
        latest = data_15m.iloc[-1]
        current_price = latest['Close']
        
        # Check RSI condition (RSI > 55 AND rising)
        rsi_above_55 = latest['RSI'] > 55 if pd.notna(latest['RSI']) else False
        rsi_rising = is_indicator_rising(data_15m['RSI'], lookback=3)
        rsi_condition = rsi_above_55 and rsi_rising
        
        # Check ADX condition (ADX > 25 AND rising)
        adx_above_25 = latest['ADX'] > 25 if pd.notna(latest['ADX']) else False
        adx_rising = is_indicator_rising(data_15m['ADX'], lookback=3)
        adx_condition = adx_above_25 and adx_rising
        
        # Check volatility condition (ATR < 2% of price AND rising)
        volatility_low = latest['ATR_Pct'] < 2.0 if pd.notna(latest['ATR_Pct']) else False
        atr_rising = is_indicator_rising(data_15m['ATR_Pct'], lookback=3)
        volatility_condition = volatility_low and atr_rising
        
        # Check other conditions
        price_ema_condition = (latest['Close'] > latest['EMA20'] > latest['EMA50'] > latest['EMA200'])
        volume_condition = latest['Volume'] > latest['Volume_MA20']
        
        conditions_met = (price_ema_condition and volume_condition and 
                         rsi_condition and adx_condition and volatility_condition)
        
        # Get trends for display
        prev_rsi = data_15m['RSI'].iloc[-2] if len(data_15m['RSI']) > 1 else None
        rsi_trend = "↑" if rsi_rising else "↓" if prev_rsi and latest['RSI'] < prev_rsi else "→"
        
        prev_adx = data_15m['ADX'].iloc[-2] if len(data_15m['ADX']) > 1 else None
        adx_trend = "↑" if adx_rising else "↓" if prev_adx and latest['ADX'] < prev_adx else "→"
        
        prev_atr = data_15m['ATR_Pct'].iloc[-2] if len(data_15m['ATR_Pct']) > 1 else None
        atr_trend = "↑" if atr_rising else "↓" if prev_atr and latest['ATR_Pct'] < prev_atr else "→"
        
        return (conditions_met, latest['ADX'], latest['RSI'], rsi_trend, 
                adx_trend, atr_trend, latest['ATR_Pct'], current_price)
        
    except Exception as e:
        print(f"Error processing {ticker_symbol} for 15m: {e}")
        return False, None, None, None, None, None, None, None

def analyze_stocks():
    """Main function to analyze stocks"""
    print("Fetching S&P 500 stocks...")
    stocks = get_sp500_stocks()
    
    print("Checking SPY condition...")
    spy_condition = check_spy_above_ema200()
    if not spy_condition:
        print("❌ SPY is not above its 200-EMA. Market condition not favorable.")
        return []
    
    print("✓ SPY is above its 200-EMA. Proceeding with analysis...")
    
    # Get SPY data for relative strength calculation
    spy = yf.Ticker('SPY')
    spy_data_daily = spy.history(period='300d', interval='1d')
    
    qualifying_stocks = []
    stock_details = []
    
    print(f"Analyzing {len(stocks)} S&P 500 stocks...")
    for i, ticker in enumerate(stocks, 1):
        print(f"Processing {ticker} ({i}/{len(stocks)})...")
        
        # Check all timeframe conditions
        daily_condition, daily_rs, daily_price = check_daily_conditions(ticker, spy_data_daily)
        condition_1h = check_1h_conditions(ticker)
        (condition_15m, adx_value, rsi_value, rsi_trend, 
         adx_trend, atr_trend, atr_pct, current_price) = check_15m_conditions(ticker)
        
        if daily_condition and condition_1h and condition_15m:
            qualifying_stocks.append(ticker)
            stock_details.append({
                'ticker': ticker,
                'daily_rs': daily_rs,
                'price': current_price,
                'adx': adx_value,
                'rsi': rsi_value,
                'rsi_trend': rsi_trend,
                'adx_trend': adx_trend,
                'atr_trend': atr_trend,
                'atr_pct': atr_pct
            })
            print(f"✓ {ticker} qualifies! Price: ${current_price:.2f}, Daily RS: {daily_rs:.3f}, ADX: {adx_value:.1f}{adx_trend}, "
                  f"RSI: {rsi_value:.1f}{rsi_trend}, ATR%: {atr_pct:.2f}%{atr_trend}")
        
        # Add delay to avoid rate limiting
        time.sleep(0.3)
    
    # Sort by daily relative strength (descending)
    if stock_details:
        stock_details.sort(key=lambda x: x['daily_rs'], reverse=True)
        qualifying_stocks = [stock['ticker'] for stock in stock_details]
    
    return qualifying_stocks, stock_details

def main():
    """Main execution function"""
    print("Stock Screening Tool - S&P 500 Analysis")
    print("=" * 100)
    print("Filters:")
    print("- Market: SPY > EMA200 (Daily)")
    print("- Daily: EMA50 > EMA200, Relative Strength > 1")
    print("- 1h: EMA50 > EMA200")
    print("- 15m: Price > EMA20 > EMA50 > EMA200, Volume > 20MA")
    print("- 15m: RSI(14) > 55 AND Rising, ADX > 25 AND Rising")
    print("- 15m: ATR% < 2.0 AND Rising (Low Volatility + Increasing Momentum)")
    print("=" * 100)
    
    start_time = datetime.now()
    results, details = analyze_stocks()
    
    print("\n" + "=" * 100)
    print("SCREENING RESULTS")
    print("=" * 100)
    
    if results:
        print(f"Qualifying stocks ({len(results)}):")
        print("\n{:<8} {:<8} {:<10} {:<12} {:<10} {:<10} {:<10} {:<10}".format(
            "Rank", "Ticker", "Price", "Daily RS", "ADX", "RSI", "ATR %", "Trends"
        ))
        print("-" * 100)
        
        for i, stock_info in enumerate(details, 1):
            trends = f"RSI{stock_info['rsi_trend']} ADX{stock_info['adx_trend']} ATR{stock_info['atr_trend']}"
            print("{:<8} {:<8} {:<10.2f} {:<12.3f} {:<10} {:<10} {:<10} {:<10}".format(
                f"#{i}", 
                stock_info['ticker'], 
                stock_info['price'],
                stock_info['daily_rs'],
                f"{stock_info['adx']:.1f}{stock_info['adx_trend']}",
                f"{stock_info['rsi']:.1f}{stock_info['rsi_trend']}",
                f"{stock_info['atr_pct']:.2f}%{stock_info['atr_trend']}",
                trends
            ))
            
        print("\n💡 Key:")
        print("   RSI Trend: ↑ = Rising, ↓ = Falling, → = Flat")
        print("   ADX Trend: ↑ = Rising, ↓ = Falling, → = Flat (ADX > 25 + Rising = Strong Trend)")
        print("   ATR Trend: ↑ = Rising volatility, ↓ = Falling volatility, → = Stable")
        print("   ATR %: Lower values indicate lower volatility (<2% is good)")
        
    else:
        print("No stocks meet all the criteria.")
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\nAnalysis completed in {duration.total_seconds():.2f} seconds")
    print(f"Analyzed all S&P 500 stocks")

if __name__ == "__main__":
    main()