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
from nautilus_trader.model.currencies import USDT, BNB
from nautilus_trader.model.instruments.currency_pair import CurrencyPair
from nautilus_trader.model.objects import Money
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity

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
    
    # CATALOG_PATH = os.getcwd() + "/catalog"
    BASE_CURR = 'BNB'
    DATA_PATH = '/Users/andrewgoldberg/nautilus_trader/data'
    CATALOG_PATH = os.path.join(DATA_PATH, BASE_CURR, 'catalog/')
    # Clear if it already exists, then create fresh
    # if os.path.exists(CATALOG_PATH):
    #     shutil.rmtree(CATALOG_PATH)
    # os.mkdir(CATALOG_PATH)
    # CATALOG_PATH = '/Users/andrewgoldberg/opt/anaconda3/envs/web3/lib/python3.9/site-packages/nautilus_trader/examples/catalog'
    catalog = ParquetDataCatalog(CATALOG_PATH)

    data_file = '/Users/andrewgoldberg/Projects/hummingbot-backtest/data/l2_data_extract_discord/BINANCE-BNB-USDT-incremental_l2_book-2022-10-13-00-00-00-2022-10-14-00-00-00.csv.gz'

    instrument = CurrencyPair(
            instrument_id=InstrumentId(
                symbol=Symbol("BNBUSDT"),
                venue=Venue("BINANCE"),
            ),
            native_symbol=Symbol("BNBUSDT"),
            base_currency=BNB,
            quote_currency=USDT,
            price_precision=2,
            size_precision=6,
            price_increment=Price(1e-02, precision=2),
            size_increment=Quantity(1e-06, precision=6),
            lot_size=None,
            max_quantity=Quantity(9000, precision=6),
            min_quantity=Quantity(1e-06, precision=6),
            max_notional=None,
            min_notional=Money(10.00000000, USDT),
            max_price=Price(1000000, precision=2),
            min_price=Price(0.01, precision=2),
            margin_init=Decimal(0),
            margin_maint=Decimal(0),
            maker_fee=Decimal("0.001"),
            taker_fee=Decimal("0.001"),
            ts_event=0,
            ts_init=0,
        )

    data_to_catalog(data_file, instrument.id, catalog)
    catalog.instruments()






