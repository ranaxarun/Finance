import vectorbt as vbt
import yfinance as yf

# Get data
df = yf.download("AAPL", period="5d", interval="1h")
close = df['Close']

# Simple strategy
entries = close > close.shift(1).fillna(False)
exits = close < close.shift(1).fillna(False)

# Backtest
pf = vbt.Portfolio.from_signals(close=close, entries=entries, exits=exits)
print(pf.stats())