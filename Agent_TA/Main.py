# Python Libraries
import pandas as pd
from Utils import Utils
import MetaTrader5 as mt5
from Decision import Decision
from connections import Connections
from RiskManager import Risk_Manager
from TrendMetrics import Trend_Metrics
from CandlesPatterns import Candles_Patterns
from TailingStoploss import Tailing_Stoploss
from MarketOrder import Market_Order_Execution
from ParameterOptimizer import Params_Optimization
from pyfiglet import Figlet

# -------------------------------------------------------------- #
# -----------________________________________________----------- #
# ----------| FIRST FUNCTIONS TO CREATE THE STRATEGY |---------- #
# ----------|________________________________________|---------- #
# -------------------------------------------------------------- #


def main(ut, auto_trade: bool, full_list: bool, ticker, params):
    
    # Risk Manager
    risk = Risk_Manager()
    # Trend Metrics
    tm = Trend_Metrics()
    tm.get_crossover(ut.data, params.BEST_FIRST_PERIOD_Ema_Cross, params.BEST_SECOND_PERIOD_Ema_Cross, params.BEST_THIRD_PERIOD_Ema_Cross, type = 1)
    tm.get_sma_bands(ut.data, params.BEST_LENGHT_Bbands ,params.BEST_STD_Bbands)
    tm.get_rsi(ut.data, ut.RSI_PERIOD, ut.OVERBOUGHT_LEVEL, ut.OVERSOLD_LEVEL)
    tm.get_volume_pvi_nvi(ut.data)
    tm.get_macd(ut.data)
    tm.combined_rsi_bollinger(ut.data, ut.SMA_PERIOD ,ut.STANDARD_DEVIATION_SMA, ut.RSI_PERIOD)
    
    # Instantiate the Candles_Patterns class
    cp = Candles_Patterns()

    # Call the methods of Candles_Patterns class
    cp.candle_basic_signal(ut.data)
    cp.engulfing(ut.data)
    cp.morning_star(ut.data)
    cp.evening_star(ut.data)
    cp.hammer(ut.data)
    cp.hanging_man(ut.data)

    # Bagging Signal
    bg = Decision(ticker)
    
    decision_signal = bg.get_decision(tm.result_df, cp.result_df)

    # ==== Results Report ==== #
    # Save dos resultados

    # Display the result dataframe
    print('Basic Information/Settings\n\n\nTrend Metrics\n{}\n\nCandle Patterns\n{}\n\nDecision\n{}\n\n'.format(tm.result_df, cp.result_df, bg.decision_df))

    if auto_trade and not full_list:        
        # Utils
        ut.get_exposure(ticker)
        tls = Tailing_Stoploss()
        tls.modify_position_tailling(risk.TAILLING_VALUE)
        
        if not mt5.positions_total() and decision_signal != 'Flat':
            
            Lot_Size = risk.market_order_size(params.WinRate_avg, ut.position_current_price)

            mk = Market_Order_Execution()
            mk.market_order(ut.tick, ticker, Lot_Size, ut.MAGIC, risk.DEFAULT_STOP_LOSS, ut.position_current_price, decision_signal)
            
            # Store Results of Metrics
            metrics_results = pd.concat([tm.result_df, cp.result_df], axis=0)
            # Connections().sql_connect(table_db_name = 'metrics_results', table=metrics_results, ifexists='append')

    elif auto_trade and full_list:

        ut.get_exposure(ticker)
        tls = Tailing_Stoploss()
        tls.modify_position_tailling(risk.TAILLING_VALUE)

        if mt5.positions_get(symbol=ticker) == () and decision_signal != 'Flat':

            Lot_Size = risk.market_order_size(params.WinRate_avg, ut.position_current_price)

            mk = Market_Order_Execution()
            mk.market_order(ut.tick, ticker, Lot_Size, ut.MAGIC, risk.DEFAULT_STOP_LOSS, ut.position_current_price, decision_signal)
            
            # Store Results of Metrics
            metrics_results = pd.concat([tm.result_df, cp.result_df], axis=0)
            # Connections().sql_connect(table_db_name = 'metrics_results', table=metrics_results, ifexists='append')

def execute_strategy():
    '''
    This function represents the execution selection according to user request 
    '''

    # Prompt the user for input 
    user_input_market_type = input("Which Type of Market should Matriz analyze? (STOCK/CAMBIAL): ").upper()
    while user_input_market_type not in ["STOCK", "CAMBIAL"]:
        print("Invalid input. Please enter 'STOCK' or 'CAMBIAL'.")
        user_input_market_type = input("Which Type of Market should Matriz analyze? (STOCK/CAMBIAL): ").upper()

    if user_input_market_type == 'CAMBIAL':
        Utils.login()

        user_timeframe_input = input("Select the TimeFrame 15M, 30M, 1H, 4h or 1D: ").upper()
        while user_input_market_type not in ["15M", "30M", "1H", "4H", "1D"]:
            print("Invalid input. Please enter '15M', '30M', '1H', '4H' or '1D'.")
            user_timeframe_input = input("Select the TimeFrame 15M, 30M, 1H, 4h or 1D: ").upper()

            # Prompt the user for input (Y/N)
            user_input_autotrade = input("Do you want to use Auto Trade? (Y/N): ").upper()
            while user_input_autotrade not in ["Y", "N", "FULL"]:
                print("Invalid input. Please enter 'Y', 'N' or 'Full'.")
                user_input_autotrade = input("Do you want to use Auto Trade? (Y/N): ").upper()

            if user_input_autotrade == 'N':
                
                user_input_ticker = input("Which ticker do you want Matriz to analyze?: ").upper()
                print(user_input_ticker)
                while True:
                    utils_instance = Utils(user_input_ticker, user_input_market_type,user_timeframe_input)        
                    main(ut=utils_instance, auto_trade=False, full_list=False, ticker=user_input_ticker)
                    
            elif user_input_autotrade == 'Y':

                user_input_ticker = input("Which ticker do you want to Auto Trade?: ").upper()
                best_params_full = Params_Optimization(user_input_ticker, user_input_market_type, user_timeframe_input).best_params   

                while True:
                    for _, row in best_params_full.iterrows():
                        utils_instance = Utils(row['Ticker'], user_input_market_type,user_timeframe_input)
                        main(ut=utils_instance, auto_trade=True, full_list=True, ticker=row['Ticker'], params=row)

            elif user_input_autotrade == 'FULL':

                tickers = mt5.symbols_get()
                tickers = pd.DataFrame(
                            [[symbol.name, symbol.description, f"{symbol.currency_base}/{symbol.currency_profit}"] for symbol in tickers],
                            columns=['Ticker', 'Description', 'Currency']
                            ) 
                
                tickers_to_process = tickers['Ticker'].head(1).tolist()
                best_params_full = Params_Optimization(tickers_to_process, user_input_market_type, user_timeframe_input).best_params   

                while True:
                    for _, row in best_params_full.iterrows():
                        utils_instance = Utils(row['Ticker'], user_input_market_type, user_timeframe_input)
                        main(ut=utils_instance, auto_trade=True, full_list=True, ticker=row['Ticker'], params=row)
                        
if __name__ == "__main__":
    execute_strategy()

# cd C:\Users\joaom\Matris\TradingRobot\Pyrobot\Application\Agent_TA   python Main.py

# Notes 
