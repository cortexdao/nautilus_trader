from decimal import Decimal
from typing import Optional
from collections import defaultdict
import pandas as pd
import os, shutil


from nautilus_trader.model.enums import BookAction
from nautilus_trader.model.enums import BookType
from nautilus_trader.model.orderbook.data import OrderBookDeltas
from nautilus_trader.model.orderbook.data import Order
from nautilus_trader.model.orderbook.data import OrderBookDelta
from nautilus_trader.model.orderbook.data import OrderBookData
# from nautilus_trader.model.orderbook.book import OrderBookData
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.backtest.data.providers import TestInstrumentProvider
from nautilus_trader.examples.strategies.market_maker import MarketMaker
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.model.enums import OMSType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.currencies import USD, USDT, BTC
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.backtest.node import BacktestNode, BacktestVenueConfig, BacktestDataConfig, BacktestRunConfig, BacktestEngineConfig
from nautilus_trader.config.common import ImportableStrategyConfig, StrategyConfig
from nautilus_trader.persistence.external.core import write_objects


if __name__ == '__main__':
    
    BIN_BTCUSDT = TestInstrumentProvider.btcusdt_binance()

    # CATALOG_PATH = os.getcwd() + "/catalog"
    CATALOG_PATH = '/Users/andrewgoldberg/opt/anaconda3/envs/web3/lib/python3.9/site-packages/nautilus_trader/examples/catalog'
    catalog = ParquetDataCatalog(CATALOG_PATH)

    write_objects(catalog, [BIN_BTCUSDT])
    print(f'catalog path: {CATALOG_PATH}')
    print(catalog.instruments())

    venues_config=[
    BacktestVenueConfig(
        name="BINANCE",
        oms_type="NETTING",
        account_type="CASH",
        book_type="L2_MBP",
        # base_currency='BTC',  # Standard single-currency account
        starting_balances=["10000 BTC", "100000 USDT"],  # Single-currency or multi-currency accounts
    )
    ]
    data_config=[
        BacktestDataConfig(
            # catalog_path=str(CATALOG_PATH),
            catalog_path=str(catalog.path),
            data_cls=str(OrderBookData.fully_qualified_name()),
            instrument_id=BIN_BTCUSDT.id.value
        )
    ]
    strategy = MarketMaker
    strategy_config = ImportableStrategyConfig(
        strategy_path=f"{strategy.__module__}:{strategy.__name__}",
        config_path=f"{strategy.__module__}:{strategy.__name__}Config",
        config=dict(
            instrument_id = str(BIN_BTCUSDT.id.value),
            trade_size = Decimal(0.003),
            max_size = Decimal(400_000_000),
        ),
    ),
    engine_config = BacktestEngineConfig(
        stratregies=[strategy_config],
        run_analysis=True,
        run_streaming=True,
    )
    config = BacktestRunConfig(
        engine=engine_config,
        data=data_config,
        venues=venues_config,
    )

    node = BacktestNode(configs=[config])

    results = node.run()
