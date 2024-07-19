import pandas as pd
import ccxt
import time
from tqdm import tqdm

file_path = 'cryptonews.csv'
df = pd.read_csv(file_path)

df['date'] = pd.to_datetime(df['date'], format='mixed')

df = df.sort_values(by='date').reset_index(drop=True)

binance = ccxt.binance()


def get_open_price(date):
    previous_minute = date - pd.Timedelta(minutes=1)
    since = binance.parse8601(previous_minute.strftime('%Y-%m-%dT%H:%M:%S'))
    ohlcv = binance.fetch_ohlcv('BTC/USDT', '1m', since, 1)
    if ohlcv:
        return ohlcv[0][1]
    else:
        return None


impact = []
for i in tqdm(range(len(df)), desc="Processing news entries"):
    current_time = df.loc[i, 'date']
    next_time = df.loc[i + 1, 'date'] if i + 1 < len(df) else current_time + pd.Timedelta(minutes=37)
    next_time = min(next_time, current_time + pd.Timedelta(minutes=37))

    current_open_price = get_open_price(current_time)
    next_open_price = get_open_price(next_time)

    if current_open_price is not None and next_open_price is not None:
        impact_value = ((next_open_price - current_open_price) / current_open_price) * 100
        impact.append(impact_value)
    else:
        impact.append(None)

df['impact'] = impact

df.to_csv('updated_cryptonews.csv', index=False)
