import pandas as pd
import requests as req
import numpy as np
from datetime import datetime
import time
import os
import shutil

def retrieve_5min_ob_candles(start_time_unix, end_time_unix, market, asset, side, data_path, time_interval):
    seconds_in_5m = 60*5
    for server_time in range(start_time_unix, end_time_unix, seconds_in_5m):
        try:
            _request = req.get(f'https://api.vantagecrypto.com/v3/1y/{market}/{asset}/ob/{side}/5m/{server_time}?api_key={api_key}')
        except:    
            time.sleep(1)
        _values = _request.json()['symbol']['Values'].split(',')

        values_lists = [minute_candle.split('/') for minute_candle in _values]
        column_names = ['DOM_0010', 'DOM_0025', 'DOM_0050', 'DOM_0100', 'DOM_1000']
        values_df = pd.DataFrame(data=values_lists, columns=column_names)

        day_5min_increments = [i for i in range(0,288*seconds_in_5m, seconds_in_5m)]
        values_df['seconds'] = day_5min_increments

        CATALOG_PATH = os.path.join(data_path, market, asset, time_interval, side)
        values_df.to_csv(f'{CATALOG_PATH}/{str(server_time)}_GMT.csv', index=False)

def build_market_asset_paths(market, data_path, time_interval):
    market_assets_json = req.get(f'https://api.vantagecrypto.com/v3/list/{market}/assets?api_key={api_key}') 
    market_assets_df = pd.DataFrame(market_assets_json.json()['assets'])
    market_assets_list = [ticker for ticker in market_assets_df.ticker]
    for asset in market_assets_list:
        CATALOG_PATH = os.path.join(data_path, market, asset, time_interval)
        if os.path.exists(CATALOG_PATH):
            continue
        else: 
            os.makedirs(CATALOG_PATH)
    return(market_assets_list)

def main(market, data_path, time_interval):
    # dir_path = os.path.join(data_path, market, asset, time_interval)

    time_now_unix = time.time()
    time_today_unix = int(datetime.date(datetime.fromtimestamp(time_now_unix)).strftime("%s"))
    seconds_in_almost_year = 60 * 60 * 24 * 364
    time_year_ago_unix = time_today_unix - seconds_in_almost_year

    market_asset_list = build_market_asset_paths(market, data_path, time_interval)
    for asset in market_asset_list:
        for side in ['bids', 'asks']:
            print(f'{asset}: {side}')
            CATALOG_PATH = os.path.join(data_path, market, asset, time_interval, side)
            if os.path.exists(CATALOG_PATH):
                continue
            else: 
                os.mkdir(CATALOG_PATH)
            retrieve_5min_ob_candles(time_year_ago_unix, time_today_unix, market, asset, side, data_path, time_interval)



if __name__ == '__main__':
    api_key = '8K4HA988PdlxisGsBPl1RB9J2KKnAtp6mzuvRJf8'
    market = 'okex'
    data_path = '/Users/andrewgoldberg/nautilus_trader/data/vantage_historical'
    time_interval = '5min'

    main(market, data_path, time_interval)


