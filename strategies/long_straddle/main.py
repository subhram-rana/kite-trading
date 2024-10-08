import time as tm

from common import utils
from strategies.long_straddle import kite_connect_client
from strategies.long_straddle.config import *
from datetime import datetime
from strategies.long_straddle.live_info import LiveInfo, TradingState
from strategies.long_straddle import config as strategy_config
from common import utils as common_util
from strategies.long_straddle.processes.entry import async_spawn_make_entry_process
from strategies.long_straddle.processes.exit import async_spawn_take_exit_process
from strategies.long_straddle.processes.live_info_display import async_spawn_live_info_viewer
from strategies.long_straddle.processes.option_price import async_spawn_option_price_fetcher
from strategies.long_straddle.processes.profit_report import async_spawn_profit_report_maker
from strategies.long_straddle.processes.stock_price import async_spawn_stock_price_fetcher
from strategies.long_straddle.processes.stoploss import async_spawn_stoploss_managing_process


def initiate_new_kite_connect_client():
    kite_connect_client.kc = utils.new_kite_connect_client()


def fetch_and_load_NSE_and_NFO_instruments():
    utils.fetch_and_load_NSE_and_NFO_instruments(kite_connect_client.kc)


def populate_initial_live_info():
    LiveInfo.date = datetime.today().date()
    LiveInfo.lot_size = common_util.get_stock_lot_size(strategy_config.STOCK_NAME)
    LiveInfo.lot_qty = strategy_config.LOT_QTY
    LiveInfo.stock_symbol = common_util.get_stock_trading_symbol_from_stock_name(strategy_config.STOCK_NAME)
    LiveInfo.stock_instrument_token = common_util.get_stock_token_from_stock_symbol(LiveInfo.stock_symbol)


def start_long_straddle_strategy():
    """ Spawns all concurrent threads and wait for trade to EXIT.
    If so it will return"""

    print('[MAIN_THREAD] : client instantiation ...')
    initiate_new_kite_connect_client()

    print('[MAIN_THREAD] : NSE and NFO instrument fetching ...')
    fetch_and_load_NSE_and_NFO_instruments()

    print('[MAIN_THREAD] : populating initial live info ...')
    populate_initial_live_info()

    # todo: remove after testing
    async_spawn_live_info_viewer()

    print('[MAIN_THREAD] : async spwanning all processes ...')
    async_spawn_stock_price_fetcher()
    async_spawn_option_price_fetcher()

    # spawnning processes in reverse dependencies
    async_spawn_profit_report_maker()
    async_spawn_take_exit_process()
    async_spawn_stoploss_managing_process()
    async_spawn_make_entry_process()

    print('[MAIN_THREAD] : waiting for trade exit .')
    while LiveInfo.trading_state != TradingState.REPORT_COMPLETED:
        tm.sleep(1)


if __name__ == '__main__':
    print('[MAIN_THREAD] : starting long-straddle strategy ...')

    start_time = datetime.now()
    start_long_straddle_strategy()
    end_time = datetime.now()

    time_taken = end_time - start_time

    print(f'[MAIN_THREAD] : Exited long-straddle strategy in time: {time_taken} !!! \n '
          f'please find the report in "reports/{SIMULATION_TYPE}.xlsx" file')

