"""
sp500_top100_screen.py

Screen 100 fixed S&P500 stocks using yfinance and the filters you requested.

Dependencies:
    pip install yfinance pandas numpy tqdm
"""

import yfinance as yf
import pandas as pd
import numpy as np
from tqdm import tqdm

# ------------------------
# Hard-coded 100 tickers (first 100 alphabetically in S&P 500)
# ------------------------
TOP100_TICKERS = [
    "A", "AAPL", "ABBV", "ABNB", "ACGL",
    "ACN", "ADBE", "ADI", "ADM", "ADP",
    "ADSK", "AEE", "AEP", "AES", "AFL",
    "AIG", "AIZ", "AJG", "AKAM", "ALB",
    "ALGN", "ALK", "ALL", "ALLE", "AMAT",
    "AMCR", "AMD", "AME", "AMGN", "AMP",
    "AMT", "AMZN", "ANET", "ANSS", "AON",
    "AOS", "APA", "APD", "APH", "APTV",
    "ARE", "ATO", "ATR", "AVB", "AVGO",
    "AVY", "AWK", "AXON", "AXP", "AZO",
    "BA", "BAC", "BALL", "BAX", "BBWI",
    "BBY", "BDX", "BEN", "BIIB", "BIO",
    "BK", "BKNG", "BKR", "BLK", "BLL",
    "BMY", "BR", "BRK-B", "BRO", "BSX",
    "BWA", "BX", "BXP", "C", "CAG",
    "CAH", "CARR", "CAT", "CB", "CBOE",
    "CBRE", "CCI", "CCL", "CDAY", "CDNS",
    "CDW", "CE", "CEG", "CF", "CFG",
    "CHD", "CHRW", "CHTR", "CI", "CINF",
    "CL", "CLX", "CMA", "CMCSA", "CME"
]

# ------------------------
# Indicator functions
# ------------------------
def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(period, min_periods=period).mean()
    ma_down = down.rolling(period, min_periods=period).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def true_range(df):
    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Close'].shift()).abs()
    tr3 = (df['Low'] - df['Close'].shift()).abs()
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

def atr(df, period=14):
    tr = true_range(df)
    return tr.rolling(period, min_periods=period).mean()

def plus_minus_dm(df):
    up_move = df['High'].diff()
    down_move = -df['Low'].diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    return pd.Series(plus_dm, index=df.index), pd.Series(minus_dm, index=df.index)

def adx(df, period=14):
    plus_dm, minus_dm = plus_minus_dm(df)
    atr_series = true_range(df).rolling(period, min_periods=period).mean()
    plus_dm_s = plus_dm.rolling(period, min_periods=period).mean()
    minus_dm_s = minus_dm.rolling(period, min_periods=period).mean()
    plus_di = 100 * (plus_dm_s / atr_series)
    minus_di = 100 * (minus_dm_s / atr_series)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    return dx.rolling(period, min_periods=period).mean()

# ------------------------
# Screening function
# ------------------------
def passes_filters(ticker, spy_daily, spy_recent_close, daily_df, hourly_df, min_df_15m):
    # --- DAILY TIMEFRAME ---
    daily_close = daily_df['Close']
    daily_ema50 = ema(daily_close, 50)
    daily_ema200 = ema(daily_close, 200)
    spy_ema200 = ema(spy_daily['Close'], 200).iloc[-1]
    if spy_recent_close <= spy_ema200:
        return False
    if not (daily_ema50.iloc[-1] > daily_ema200.iloc[-1]):
        return False
    # Relative strength
    lookback = 50
    if len(daily_close) < lookback + 1:
        return False
    stock_ret = daily_close.iloc[-1] / daily_close.shift(lookback).iloc[-1]
    spy_ret = spy_daily['Close'].iloc[-1] / spy_daily['Close'].shift(lookback).iloc[-1]
    rs = stock_ret / spy_ret if spy_ret != 0 else 0
    if not (rs > 1):
        return False

    # --- 1-HOUR ---
    if len(hourly_df) < 200:
        return False
    h_close = hourly_df['Close']
    h_ema50 = ema(h_close, 50).iloc[-1]
    h_ema200 = ema(h_close, 200).iloc[-1]
    if not (h_ema50 > h_ema200):
        return False

    # --- 15-MINUTE ---
    if len(min_df_15m) < 200:
        return False
    m_close = min_df_15m['Close']
    m_vol = min_df_15m['Volume']
    ema20 = ema(m_close, 20).iloc[-1]
    ema50 = ema(m_close, 50).iloc[-1]
    ema200 = ema(m_close, 200).iloc[-1]
    last_price = m_close.iloc[-1]
    if not (last_price > ema20 > ema50 > ema200):
        return False
    vol20 = m_vol.rolling(20, min_periods=10).mean().iloc[-1]
    if not (m_vol.iloc[-1] > vol20):
        return False
    m_rsi = rsi(m_close, 14)
    if not (m_rsi.iloc[-1] > 55 and m_rsi.iloc[-1] > m_rsi.shift(3).iloc[-1]):
        return False
    m_adx = adx(min_df_15m[['High','Low','Close']], 14)
    if not (m_adx.iloc[-1] > 25 and m_adx.iloc[-1] > m_adx.shift(3).iloc[-1]):
        return False
    m_atr = atr(min_df_15m[['High','Low','Close']], 14)
    atr_pct = (m_atr / m_close) * 100
    if not (atr_pct.iloc[-1] < 2.0 and atr_pct.iloc[-1] > atr_pct.shift(3).iloc[-1]):
        return False

    return True

# ------------------------
# Main
# ------------------------
def main():
    print("Using hard-coded first 100 S&P 500 tickers:")
    print(TOP100_TICKERS)

    spy = yf.Ticker("SPY")
    spy_daily = spy.history(period="2y", interval="1d")
    spy_recent_close = spy_daily['Close'].iloc[-1]

    passing = []
    for t in tqdm(TOP100_TICKERS, desc="Screening top100"):
        try:
            daily_df = yf.download(t, period="2y", interval="1d", progress=False)
            hourly_df = yf.download(t, period="180d", interval="60m", progress=False)
            min15_df = yf.download(t, period="60d", interval="15m", progress=False)
            if daily_df.empty or hourly_df.empty or min15_df.empty:
                continue
            if passes_filters(t, spy_daily, spy_recent_close, daily_df, hourly_df, min15_df):
                passing.append(t)
        except Exception:
            continue

    print("\nStocks that passed all filters:")
    print(passing)

if __name__ == "__main__":
    main()
