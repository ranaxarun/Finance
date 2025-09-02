import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout

# Download data from Yahoo Finance
def download_stock_data(ticker, period='1y'):
    """Download stock data from Yahoo Finance"""
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

# Prepare data for LSTM model
def prepare_data(data, lookback=60):
    """Prepare data for training"""
    # Use only the 'Close' price
    dataset = data['Close'].values.reshape(-1, 1)
    
    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)
    
    # Create training data
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i, 0])
        y.append(scaled_data[i, 0])
    
    X, y = np.array(X), np.array(y)
    
    # Reshape for LSTM [samples, time steps, features]
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    
    return X, y, scaler

# Build LSTM model
def build_model(lookback):
    """Build LSTM model"""
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(lookback, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Main execution
def main():
    # Parameters
    TICKER = 'AAPL'  # Apple stock
    LOOKBACK = 60    # Use 60 days to predict next day
    TRAIN_SPLIT = 0.8  # 80% for training, 20% for testing
    
    print("Downloading stock data...")
    # Download stock data
    data = download_stock_data(TICKER, period='2y')  # 2 years of data
    
    if data.empty:
        print("No data downloaded. Please check the ticker symbol.")
        return
    
    print("Preparing data...")
    # Prepare data
    X, y, scaler = prepare_data(data, LOOKBACK)
    
    # Split data into train and test sets
    split_index = int(len(X) * TRAIN_SPLIT)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]
    
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Build and train model
    print("Building and training model...")
    model = build_model(LOOKBACK)
    
    # Train the model
    history = model.fit(X_train, y_train, 
                       batch_size=32, 
                       epochs=50, 
                       validation_data=(X_test, y_test),
                       verbose=1)
    
    # Make predictions
    print("Making predictions...")
    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)
    
    # Inverse transform predictions
    train_predictions = scaler.inverse_transform(train_predictions)
    test_predictions = scaler.inverse_transform(test_predictions)
    y_train_actual = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_actual = scaler.inverse_transform(y_test.reshape(-1, 1))
    
    # Plot results
    plt.figure(figsize=(14, 6))
    
    # Plot training data
    train_plot = np.empty_like(data['Close'])
    train_plot[:] = np.nan
    train_plot[LOOKBACK:LOOKBACK + len(train_predictions)] = train_predictions.flatten()
    
    # Plot test data
    test_plot = np.empty_like(data['Close'])
    test_plot[:] = np.nan
    test_plot[LOOKBACK + len(train_predictions):LOOKBACK + len(train_predictions) + len(test_predictions)] = test_predictions.flatten()
    
    plt.plot(data['Close'].values, label='Actual Price')
    plt.plot(train_plot, label='Training Predictions')
    plt.plot(test_plot, label='Testing Predictions')
    
    plt.title(f'{TICKER} Stock Price Prediction')
    plt.xlabel('Time')
    plt.ylabel('Price ($)')
    plt.legend()
    plt.show()
    
    # Predict next day
    last_60_days = data['Close'][-LOOKBACK:].values.reshape(-1, 1)
    last_60_days_scaled = scaler.transform(last_60_days)
    
    X_pred = np.array([last_60_days_scaled.flatten()])
    X_pred = np.reshape(X_pred, (X_pred.shape[0], X_pred.shape[1], 1))
    
    predicted_price = model.predict(X_pred)
    predicted_price = scaler.inverse_transform(predicted_price)
    
    print(f"\nLast actual price: ${data['Close'].iloc[-1]:.2f}")
    print(f"Predicted next day price: ${predicted_price[0][0]:.2f}")

if __name__ == "__main__":
    main()