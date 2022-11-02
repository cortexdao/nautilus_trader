from nautilus_trader.model.enums import BookAction
from nautilus_trader.model.enums import BookType
from nautilus_trader.model.orderbook.data import Order
from nautilus_trader.model.orderbook.data import OrderBookDelta
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.backtest.data.providers import TestInstrumentProvider
from collections import defaultdict
from nautilus_trader.examples.strategies.market_maker import MarketMaker
from nautilus_trader.persistence.external.core import process_files
from nautilus_trader.persistence.external.readers import CSVReader
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from decimal import Decimal
import os, shutil
import pandas as pd

def parser(data, instrument_id):
    """ Parser function for hist_data FX data, for use with CSV Reader """
    # dt = pd.Timestamp(datetime.datetime.strptime(data['timestamp'].decode(), "%Y%m%d %H%M%S%f"), tz='UTC')

    side_to_code = {
    'bid': 1,
    'ask': 2
    }
    yield OrderBookDelta(
        instrument_id=instrument_id,
        book_type=BookType.L2_MBP,
        action=BookAction.DELETE if data['amount'].decode()== 0 else BookAction.UPDATE, 
        order=Order(
                    price=int(float(data['price'].decode())),
                    size=int(float(data['amount'].decode())),
                    side=side_to_code[data['side'].decode()],
                    # side=side_to_code[data['side'].decode()]
                ),
                ts_event=int(data['timestamp'].decode()) *1000,
                ts_init=int(data['timestamp'].decode()) *1000
    )

def data_to_catalog(data_path, instrument_id, _catalog):
    """ Reads .csv data file into parquet catalog """
    process_files(
        glob_path=data_path,
        reader=CSVReader(
            block_parser=lambda x: parser(x, instrument_id=instrument_id), 
            header=None,
            chunked=False, 
            as_dataframe=False,
        ),
        catalog=_catalog,
    )


if __name__ == '__main__':

    data_file = '/Users/andrewgoldberg/Projects/hummingbot-backtest/data/l2_data_extract_discord/BINANCE-BNB-USDT-incremental_l2_book-2022-10-13-00-00-00-2022-10-14-00-00-00.csv.gz'
    # data_df = pd.read_csv(data_file, compression='gzip', error_bad_lines=False)

    CATALOG_PATH = os.getcwd() + "/catalog"

    # Clear if it already exists, then create fresh
    # if os.path.exists(CATALOG_PATH):
    #     shutil.rmtree(CATALOG_PATH)
    # os.mkdir(CATALOG_PATH)

    catalog = ParquetDataCatalog(CATALOG_PATH)

    from nautilus_trader.persistence.external.core import process_files, write_objects
    from nautilus_trader.backtest.data.providers import TestInstrumentProvider

    # BIN_BTCUSDT = TestInstrumentProvider.btcusdt_binance()
    BIN_BNBUSDT = instrument

    from nautilus_trader.persistence.external.core import write_objects

    write_objects(catalog, [BIN_BNBUSDT])

    catalog.instruments()






