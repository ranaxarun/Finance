import yfinance as yf
import pandas as pd
import ta
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


# -------------------------------
# Step 1: Get S&P 500 Tickers
# -------------------------------
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    tables = pd.read_html(response.text)
    df = tables[0]
    return df['Symbol'].tolist()


# -------------------------------
# Step 2: Worker function
# -------------------------------
def process_ticker(ticker):
    try:
        # --- 15m data ---
        data_15m = yf.download(
            ticker, interval="15m", period="20d", progress=False, auto_adjust=False
        )
        if data_15m.empty:
            return None

        close_15m = data_15m["Close"].squeeze()
        volume_15m = data_15m["Volume"].squeeze()

        # EMAs
        data_15m["EMA20"] = ta.trend.EMAIndicator(close_15m, window=20).ema_indicator()
        data_15m["EMA50"] = ta.trend.EMAIndicator(close_15m, window=50).ema_indicator()
        data_15m["EMA200"] = ta.trend.EMAIndicator(close_15m, window=200).ema_indicator()

        # RSI
        data_15m["RSI"] = ta.momentum.RSIIndicator(close_15m, window=14).rsi()

        last_close_15m = close_15m.iloc[-1]
        last_ema20_15m = data_15m["EMA20"].iloc[-1]
        last_ema50_15m = data_15m["EMA50"].iloc[-1]
        last_ema200_15m = data_15m["EMA200"].iloc[-1]
        last_rsi = data_15m["RSI"].iloc[-1]

        # Condition A: Price > EMA20 > EMA50 > EMA200
        condition_15m = last_close_15m > last_ema20_15m > last_ema50_15m > last_ema200_15m
        if not condition_15m:
            return None

        # Buying Pressure: Latest volume > 20-period average volume
        avg_vol = volume_15m.rolling(window=20).mean().iloc[-1]
        last_vol = volume_15m.iloc[-1]
        condition_volume = last_vol > avg_vol
        if not condition_volume:
            return None

        # RSI Filter: RSI > 55
        condition_rsi = last_rsi > 55
        if not condition_rsi:
            return None

        # --- 1h data ---
        data_1h = yf.download(
            ticker, interval="1h", period="200d", progress=False, auto_adjust=False
        )
        if data_1h.empty:
            return None

        close_1h = data_1h["Close"].squeeze()
        data_1h["EMA50"] = ta.trend.EMAIndicator(close_1h, window=50).ema_indicator()
        data_1h["EMA200"] = ta.trend.EMAIndicator(close_1h, window=200).ema_indicator()

        last_ema50_1h = data_1h["EMA50"].iloc[-1]
        last_ema200_1h = data_1h["EMA200"].iloc[-1]

        # Condition B: 1h EMA50 > EMA200
        condition_1h = last_ema50_1h > last_ema200_1h

        if condition_15m and condition_volume and condition_rsi and condition_1h:
            return (
                ticker,
                last_close_15m,
                last_ema20_15m,
                last_ema50_15m,
                last_ema200_15m,
                last_vol,
                avg_vol,
                last_rsi,
                last_ema50_1h,
                last_ema200_1h,
            )

    except Exception as e:
        print(f"Error with {ticker}: {e}")
    return None


# -------------------------------
# Step 3: Run Multi-threaded Scan
# -------------------------------
def check_stocks_multi_tf():
    tickers = get_sp500_tickers()
    results = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_ticker, t): t for t in tickers}
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    return results


# -------------------------------
# Step 4: Main
# -------------------------------
if __name__ == "__main__":
    stocks = check_stocks_multi_tf()
    print("Stocks matching conditions:")
    print(" (15m: Price > EMA20 > EMA50 > EMA200) "
          "AND (Volume > 20-period avg) "
          "AND (RSI > 55) "
          "AND (1h: EMA50 > EMA200)\n")

    for s in stocks:
        print(
            f"{s[0]} → Price: {s[1]:.2f}, 15m_EMA20: {s[2]:.2f}, "
            f"15m_EMA50: {s[3]:.2f}, 15m_EMA200: {s[4]:.2f}, "
            f"LastVol: {s[5]:.0f}, AvgVol20: {s[6]:.0f}, RSI: {s[7]:.2f}, "
            f"1h_EMA50: {s[8]:.2f}, 1h_EMA200: {s[9]:.2f}"
        )

    # Save to CSV
    pd.DataFrame(
        stocks,
        columns=[
            "Ticker", "Price", "15m_EMA20", "15m_EMA50", "15m_EMA200",
            "LastVol", "AvgVol20", "RSI", "1h_EMA50", "1h_EMA200"
        ]
    ).to_csv("stocks_multi_tf_buying_pressure_rsi.csv", index=False)

    print("\n✅ Results saved to stocks_multi_tf_buying_pressure_rsi.csv")
