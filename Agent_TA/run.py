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

# -------------------------------------------------------------- #
# -----------________________________________________----------- #
# ----------| FIRST FUNCTIONS TO CREATE THE STRATEGY |---------- #
# ----------|________________________________________|---------- #
# -------------------------------------------------------------- #

class engine():
    def __init__(self) -> None:
        pass 

    def main(self, ut, auto_trade: bool, full_list: bool, ticker, params):
        
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

    def execute_strategy(self, market_type, timeframe, ticker, autotrade_set, stop):
        '''
        This function represents the execution selection according to user request 
        '''
        
        if market_type == 'Cambial':
            Utils.login()
        
        
            if ticker == 'Top10':
                if autotrade_set == 'on': 
                    while stop == False:
                        tickers = mt5.symbols_get()
                        tickers = pd.DataFrame(
                                    [[symbol.name, symbol.description, f"{symbol.currency_base}/{symbol.currency_profit}"] for symbol in tickers],
                                    columns=['Ticker', 'Description', 'Currency']
                                    ) 
                        
                        tickers_to_process = tickers['Ticker'].head(10).tolist()
                        best_params_top10 = Params_Optimization(tickers_to_process, market_type, timeframe).best_params   

                        for _, row in best_params_top10.iterrows():
                            utils_instance = Utils(row['Ticker'], market_type, timeframe)
                            self.main(ut=utils_instance, auto_trade=True, full_list=True, ticker=row['Ticker'], params=row)
                
                elif autotrade_set == 'off': 
                    while stop == False:
                        tickers = mt5.symbols_get()
                        tickers = pd.DataFrame(
                                    [[symbol.name, symbol.description, f"{symbol.currency_base}/{symbol.currency_profit}"] for symbol in tickers],
                                    columns=['Ticker', 'Description', 'Currency']
                                    ) 
                        
                        tickers_to_process = tickers['Ticker'].head(10).tolist()
                        best_params_top10 = Params_Optimization(tickers_to_process, market_type, timeframe).best_params   

                        for _, row in best_params_top10.iterrows():
                            utils_instance = Utils(row['Ticker'], market_type, timeframe)
                            self.main(ut=utils_instance, auto_trade=False, full_list=False, ticker=row['Ticker'], params=row)
            
            elif ticker == 'Crypto':
                crypto = pd.DataFrame([[symbol.name, symbol.path] for symbol in mt5.symbols_get()], columns = ['Ticker', 'Path'])
                crypto = crypto[crypto['Path'].str.contains("crypto", case=False)]
                tickers_to_process = crypto['Ticker'].tolist()

                best_params_top10 = Params_Optimization(tickers_to_process, market_type, timeframe).best_params   

                for _, row in best_params_top10.iterrows():
                    utils_instance = Utils(row['Ticker'], market_type, timeframe)
                    self.main(ut=utils_instance, auto_trade=False, full_list=False, ticker=row['Ticker'], params=row)
    
            else:
                if autotrade_set == 'on': 
                    
                    best_params = Params_Optimization(ticker, market_type, timeframe).best_params   
                    while stop == False:
                        for _, row in best_params.iterrows():
                            utils_instance = Utils(row['Ticker'], market_type, timeframe)
                            self.main(ut=utils_instance, auto_trade=True, full_list=False, ticker=row['Ticker'], params=row)

                elif autotrade_set == 'off': 
                    
                    best_params = Params_Optimization(ticker, market_type, timeframe).best_params   
                    while stop == False:
                        for _, row in best_params.iterrows():
                            utils_instance = Utils(row['Ticker'], market_type, timeframe)
                            self.main(ut=utils_instance, auto_trade=False, full_list=False, ticker=row['Ticker'], params=row)



    # cd C:\Users\joaom\Matris\TradingRobot\Pyrobot\Application\Agent_TA   python Main.py

    # Notes 
