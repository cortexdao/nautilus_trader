from decimal import Decimal
from typing import Optional
from collections import defaultdict
import pandas as pd

from nautilus_trader.model.enums import BookAction
from nautilus_trader.model.enums import BookType
from nautilus_trader.model.orderbook.data import OrderBookDeltas
from nautilus_trader.model.orderbook.data import Order
from nautilus_trader.model.orderbook.data import OrderBookDelta
from nautilus_trader.model.orderbook.book import OrderBook
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


if __name__ == '__main__':
    
    bin_btcusdt_ticks_file = ''
    data_file = '../../data/l2_data_extract_discord/BINANCE-BTC-USDT-incremental_l2_book-2022-10-13-00-00-00-2022-10-14-00-00-00.csv.gz'
    data_file = '/Users/andrewgoldberg/Projects/hummingbot-backtest/data/l2_data_extract_discord/BINANCE-BTC-USDT-incremental_l2_book-2022-10-13-00-00-00-2022-10-14-00-00-00.csv.gz'
    data_df = pd.read_csv(data_file, nrows=10000, compression='gzip', error_bad_lines=False)


    side_to_code = {
        'bid': 1,
        'ask': 2
    }

    BIN_BTCUSDT = TestInstrumentProvider.btcusdt_binance()

    alldeltas = []
    for ts in data_df.timestamp.unique():
        deltas = []
        for idx, row in data_df[data_df.timestamp==ts].iterrows():
            delta_ = OrderBookDelta(
                instrument_id=BIN_BTCUSDT.id,
                book_type=BookType.L2_MBP,
                action=BookAction.DELETE if row.amount == 0 else BookAction.UPDATE,
                order=Order(
                    price=row['price'],
                    size=row['amount'],
                    side=side_to_code[row['side']]
                ),
                ts_event=ts*1000,
                ts_init=ts*1000
            )
            deltas.append(delta_)
        alldeltas.append(
            OrderBookDeltas(
                book_type=BookType.L2_MBP,
                instrument_id=BIN_BTCUSDT.id,
                deltas=deltas,
                ts_event=ts*1000,
                ts_init=ts*1000,
            )
            )

    print('start')
    # Configure backtest engine
    config = BacktestEngineConfig(
        trader_id="BACKTESTER-001",
    )
    print('config')
    # Build the backtest engine
    engine = BacktestEngine(config=config)
    print('set config')
    # Add a trading venue (multiple venues possible)
    engine.add_venue(
        venue=BIN_BTCUSDT.venue,
        oms_type=OMSType.NETTING,
        account_type=AccountType.CASH,
        book_type=2,
        base_currency=None,  # Standard single-currency account
        starting_balances=[Money(10_000_000, BTC), Money(10_000_000, USDT)],  # Single-currency or multi-currency accounts
    )
    print('add venue')
    # Add instruments
    engine.add_instrument(BIN_BTCUSDT)
    print('add instrument')
    # Add data
    engine.add_data(alldeltas)
    print('add deltas data')
    strategy = MarketMaker(
        instrument_id = BIN_BTCUSDT.id,
        trade_size = Decimal(0.003),
        max_size = Decimal(400_000_000),
    )
    print('set marketmaker strateg')
    # strategy = VolatilityMarketMaker(config=config)
    engine.add_strategy(strategy=strategy)
    print('add strategy')
    # input("Press Enter to continue...")  # noqa (always Python 3)

    # Run the engine (from start to end of data)
    engine.run()
    print('run streaming')
    # Optionally view reports
    with pd.option_context(
        "display.max_rows",
        100,
        "display.max_columns",
        None,
        "display.width",
        300,
    ):
        print(engine.trader.generate_account_report(BIN_BTCUSDT.venue))
        print(engine.trader.generate_order_fills_report())
        print(engine.trader.generate_positions_report())

    # For repeated backtest runs make sure to reset the engine
    engine.reset()

    # Good practice to dispose of the object when done
    engine.dispose()