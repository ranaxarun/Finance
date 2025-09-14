import yfinance as yf
import pandas as pd
import datetime

# Full S&P 500 tickers (as before)
tickers = [
    "A", "AAPL", "ABBV", "ABNB", "ACGL", "ACN", "ADBE", "ADI", "ADM", "ADP",
    "ADSK", "AEE", "AEP", "AES", "AFL", "AIG", "AIZ", "AJG", "AKAM", "ALB",
    "ALGN", "ALK", "ALL", "AMAT", "AMD", "AME", "AMGN", "AMP", "AMT", "AMZN",
    "ANET", "ANSS", "AON", "AOS", "APA", "APD", "APH", "APO", "APP", "APTV",
    "ARE", "ATO", "AVB", "AVGO", "AVY", "AWK", "AXON", "AXP", "AZO", "BA",
    "BAC", "BALL", "BAX", "BBWI", "BBY", "BDX", "BEN", "BG", "BIIB", "BIO",
    "BK", "BKNG", "BKR", "BLDR", "BLK", "BMY", "BR", "BRK-B", "BRO", "BSX",
    "BWA", "BX", "BXP", "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE",
    "CBRE", "CCI", "CCL", "CDAY", "CDNS", "CDW", "CE", "CEG", "CF", "CFG",
    "CHD", "CHRW", "CHTR", "CI", "CINF", "CL", "CLX", "CMA", "CMCSA", "CME",
    "CMG", "CMS", "CNC", "CNP", "COF", "COO", "COP", "COST", "CPAY", "CPB",
    "CPRT", "CPT", "CRL", "CRM", "CSCO", "CSGP", "CSX", "CTAS", "CTLT", "CTRA",
    "CTSH", "CTVA", "CVS", "CVX", "CZR", "D", "DAL", "DD", "DE", "DECK",
    "DFS", "DG", "DGX", "DHI", "DHR", "DIS", "DLR", "DLTR", "DOV", "DOW",
    "DPZ", "DRI", "DTE", "DUK", "DVA", "DVN", "DXCM", "EA", "EBAY", "ECL",
    "ED", "EFX", "EIX", "EL", "ELV", "EMN", "EMR", "ENPH", "EOG", "EQIX",
    "EQR", "EQT", "ES", "ESS", "ETN", "ETR", "ETSY", "EVRG", "EXC", "EXPD",
    "EXPE", "EXR", "F", "FANG", "FAST", "FCX", "FDS", "FDX", "FE", "FFIV",
    "FICO", "FIS", "FISV", "FITB", "FLR", "FMC", "FOX", "FOXA", "FRT", "FSLR",
    "FTNT", "FTV", "GD", "GE", "GEHC", "GEN", "GILD", "GIS", "GL", "GLW",
    "GM", "GNRC", "GOOG", "GOOGL", "GPC", "GPN", "GRMN", "GS", "GWW", "HAL",
    "HAS", "HBAN", "HCA", "HD", "HES", "HIG", "HII", "HLT", "HOLX", "HON",
    "HPE", "HPQ", "HRL", "HSIC", "HST", "HSY", "HUBB", "HUM", "HWM", "IBM",
    "ICE", "IDXX", "IEX", "IFF", "ILMN", "INCY", "INTC", "INTU", "INVH", "IP",
    "IPG", "IQV", "IR", "IRM", "ISRG", "IT", "ITW", "IVZ", "J", "JBHT",
    "JCI", "JKHY", "JNJ", "JNPR", "JPM", "K", "KDP", "KEY", "KEYS", "KHC",
    "KIM", "KLAC", "KMB", "KMI", "KMX", "KO", "KR", "KVUE", "L", "LDOS",
    "LEN", "LH", "LHX", "LIN", "LKQ", "LLY", "LMT", "LNC", "LNT", "LOW",
    "LRCX", "LULU", "LUV", "LYB", "LYV", "MA", "MAA", "MAR", "MAS", "MCD",
    "MCHP", "MCK", "MCO", "MDLZ", "MDT", "MET", "META", "MGM", "MHK", "MKC",
    "MKTX", "MLM", "MMC", "MMM", "MNST", "MO", "MOS", "MPC", "MPWR", "MRK",
    "MRNA", "MRO", "MS", "MSCI", "MSFT", "MSI", "MTB", "MTCH", "MTD", "MU",
    "NCLH", "NDAQ", "NDSN", "NEE", "NEM", "NFLX", "NI", "NKE", "NOC", "NOW",
    "NRG", "NSC", "NTAP", "NTRS", "NUE", "NVDA", "NVR", "NWS", "NWSA", "NXPI",
    "O", "ODFL", "OKE", "OMC", "ON", "ORCL", "ORLY", "OTIS", "OXY", "PANW",
    "PARA", "PAYC", "PAYX", "PCAR", "PCG", "PEG", "PEP", "PFE", "PFG", "PG",
    "PGR", "PH", "PHM", "PKG", "PLD", "PLTR", "PM", "PNC", "PNR", "PNW",
    "PODD", "POOL", "PPG", "PPL", "PRU", "PSA", "PSX", "PTC", "PWR", "PXD",
    "PYPL", "QCOM", "QRVO", "RCL", "REG", "REGN", "RF", "RHI", "RJF", "RL",
    "RMD", "ROK", "ROL", "ROP", "ROST", "RSG", "RTX", "RVTY", "SBAC", "SBUX",
    "SCHW", "SEDG", "SEE", "SHW", "SJM", "SLB", "SNA", "SNPS", "SO", "SPG",
    "SPGI", "SRE", "STE", "STLD", "STT", "STX", "STZ", "SWK", "SWKS", "SYF",
    "SYK", "SYY", "T", "TAP", "TDG", "TDY", "TECH", "TEL", "TER", "TFC",
    "TFX", "TGT", "TJX", "TMO", "TMUS", "TPR", "TRGP", "TRMB", "TROW", "TRV",
    "TSCO", "TSLA", "TSN", "TT", "TTWO", "TXN", "TXT", "TYL", "UAL", "UDR",
    "UHS", "ULTA", "UNH", "UNP", "UPS", "URI", "USB", "V", "VFC", "VICI",
    "VLO", "VLTO", "VMC", "VRSK", "VRSN", "VRTX", "VTR", "VTRS", "VZ", "WAB",
    "WAT", "WBA", "WBD", "WDC", "WEC", "WELL", "WFC", "WHR", "WM", "WMB",
    "WMT", "WRB", "WRK", "WST", "WTW", "WY", "WYNN", "XEL", "XOM", "XRAY",
    "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS"
]

# Date range (~90 days back for 1h data)
end_date = datetime.datetime.today()
start_date = end_date - datetime.timedelta(days=90)

# Cutoff date (naive datetime) — we’ll align per ticker’s index tz
cutoff_date = datetime.datetime(2025, 9, 12)

results = []

for ticker in tickers:
    try:
        # Download 1-hour data
        df = yf.download(ticker, start=start_date, end=end_date, interval="1h", progress=False)

        if df.empty:
            print(f"No data for {ticker}")
            continue

        # Compute EMAs
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()

        # Detect golden cross (EMA50 crossing above EMA200)
        df["Signal"] = (df["EMA50"] > df["EMA200"]) & (df["EMA50"].shift(1) <= df["EMA200"].shift(1))

        # Get signal index
        signal_idx = df[df["Signal"]].index

        latest_cross = None
        close_at_cross = None
        if len(signal_idx) > 0:
            # Handle tz-aware vs tz-naive
            if signal_idx.tz is not None:
                cutoff_ts = pd.Timestamp(cutoff_date).tz_localize(signal_idx.tz)
                valid_crosses = [d for d in signal_idx if d > cutoff_ts]
            else:
                valid_crosses = [d for d in signal_idx if d > cutoff_date]

            if valid_crosses:
                latest_dt = max(valid_crosses)
                latest_cross = latest_dt.strftime('%Y-%m-%d %H:%M')
                close_at_cross = df.loc[latest_dt, "Close"]

        if latest_cross:
            results.append({
                "Ticker": ticker,
                "Latest Crossover": latest_cross,
                "Close at Crossover": close_at_cross
            })

    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# Save results
output_df = pd.DataFrame(results)
output_df.to_csv("golden_cross_results_1h_ema_latest.csv", index=False)

print("✅ Scan complete. Latest EMA golden cross with close price saved to golden_cross_results_1h_ema_latest.csv")
