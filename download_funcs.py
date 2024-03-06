import pandas as pd
import numpy as np
from binance.client import Client

# DOWNLOAD DATA
def download_symbol(symbol, interval, days_ago=10000, save_path='./'):
    # Initialize Binance client
    client = Client('', '')

    # Get historical klines
    klines = client.get_historical_klines(symbol, interval, f"{days_ago} days ago")

    # Create a DataFrame
    df = pd.DataFrame(klines, columns=['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

    # Convert timestamps to datetime
    df['DateTime'] = pd.to_datetime(df['DateTime'], unit='ms')

    # Convert columns to appropriate data types for calculations
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].apply(pd.to_numeric)
    df = df[['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df.set_index('DateTime', inplace=True)
    df.replace(0, np.nan, inplace=True)

    # Reindex the DataFrame with the complete index
    complete_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq=interval)
    df = pd.concat([df, pd.DataFrame(index=complete_index)], axis=1)

    # Interpolate the missing values linearly
    df.interpolate(method='linear', inplace=True)

    # Save to CSV file
    if save_path:
        csv_file = save_path+symbol+'_'+interval+'.csv'
        df.to_csv(csv_file, index_label='DateTime')
        print('Download done and saved in: ', csv_file)

    return df

#download_symbol('BTCUSDT', '4h', days_ago=10000, save_path='./')