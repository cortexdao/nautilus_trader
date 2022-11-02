from nautilus_trader.model.enums import BookAction
from nautilus_trader.model.enums import BookType
from nautilus_trader.model.orderbook.data import OrderBookDeltas
from nautilus_trader.model.orderbook.data import Order
from nautilus_trader.model.orderbook.data import OrderBookDelta
from nautilus_trader.model.orderbook.book import OrderBook
# from nautilus_trader.model.orderbook.book import L2OrderBook
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.backtest.data.providers import TestInstrumentProvider
from collections import defaultdict
from nautilus_trader.examples.strategies.market_maker import MarketMaker
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.enums import OMSType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.currencies import USD, USDT, BTC, BNB
from nautilus_trader.model.instruments.currency_pair import CurrencyPair
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.persistence.external.core import process_files
from nautilus_trader.persistence.external.readers import CSVReader
from decimal import Decimal
import os, shutil
import pandas as pd

if __name__ == '__main__':

    data_file = '/Users/andrewgoldberg/Projects/hummingbot-backtest/data/l2_data_extract_discord/BINANCE-BNB-USDT-incremental_l2_book-2022-10-13-00-00-00-2022-10-14-00-00-00.csv.gz'
    data_df = pd.read_csv(data_file, compression='gzip', error_bad_lines=False)

    CATALOG_PATH = os.getcwd() + "/catalog"

    # Clear if it already exists, then create fresh
    # if os.path.exists(CATALOG_PATH):
    #     shutil.rmtree(CATALOG_PATH)
    # os.mkdir(CATALOG_PATH)

    from nautilus_trader.persistence.catalog import ParquetDataCatalog
    catalog = ParquetDataCatalog(CATALOG_PATH)

    from nautilus_trader.persistence.external.core import process_files, write_objects
    from nautilus_trader.backtest.data.providers import TestInstrumentProvider

    # BIN_BTCUSDT = TestInstrumentProvider.btcusdt_binance()
    BIN_BNBUSDT = instrument

    from nautilus_trader.persistence.external.core import write_objects

    write_objects(catalog, [BIN_BNBUSDT])

    catalog.instruments()


side_to_code = {
    'bid': 1,
    'ask': 2
}

def parser(data, instrument_id):
    """ Parser function for hist_data FX data, for use with CSV Reader """
    # dt = pd.Timestamp(datetime.datetime.strptime(data['timestamp'].decode(), "%Y%m%d %H%M%S%f"), tz='UTC')
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




process_files(
    glob_path=data_file,
    reader=CSVReader(
        block_parser=lambda x: parser(x, instrument_id=BIN_BNBUSDT.id), 
        header=None,
        chunked=False, 
        as_dataframe=False,
    ),
    catalog=catalog,
)

