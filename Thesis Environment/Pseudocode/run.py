# Python Libraries
import time
import pandas as pd
from Utils import Utils
import MetaTrader5 as mt5
import Config as config
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
        
        # Trend Metrics
        tm = Trend_Metrics()
        tm.get_crossover(ut.data, params.Best_Ema1_Cross, params.Best_Ema2_Cross, params.Best_Ema3_Cross)
        tm.get_sma_bands(ut.data, params.Best_Ema1_Bbands ,params.Best_std_Bbands)
        tm.get_rsi(ut.data, params.Best_Ema1_Bbands, params.Rsi_overbought, params.Rsi_oversold)
        tm.get_volume_profile(ut.data_1h)
        
        # Instantiate the Candles_Patterns class
        cp = Candles_Patterns()
        cp.candle_basic_signal(ut.data)
        cp.engulfing(ut.data)
        cp.morning_star(ut.data)
        cp.evening_star(ut.data)
        cp.hammer(ut.data)
        cp.hanging_man(ut.data)

        # Risk Manager
        risk = Risk_Manager()        
        stloss = risk.risk_manager(cp.result_df)

        # Bagging Signal
        decision_signal = risk.get_decision(tm.result_df, cp.result_df)

        # ==== Results Report ==== #
        print('\033[91mBasic Information/Settings:\033[0m\n\n   \
              \033[91mTrend Metrics:\033[0m\n{}\n\n \
              Support: {}\n \
              Resistence: {}\n\n \
              \033[91mCandle Patterns:\033[0m\n{}\n\n  \
              \033[91mDecision:\033[0m\n{}\n\n  \
              \033[91mCriteria:\033[0m\n{}\n\n' \
              .format(tm.result_df, tm.support, tm.resistence, cp.result_df, decision_signal, params))
        
        time.sleep(2)

        if auto_trade and not full_list:        

            ut.get_exposure(ticker)
            if stloss == "tail":
                tls = Tailing_Stoploss()
                tls.modify_position_tailling(sup=tm.support, resis=tm.resistence, tailling_value = 0.01)
                if not mt5.positions_total() and decision_signal == 'Sell':
                    mk = Market_Order_Execution()
                    mk.market_order(ut.tick, ticker, 0.01, tm.support, ut.position_current_price, decision_signal, ut.VOLUME, ut.MAGIC)
                if not mt5.positions_total() and decision_signal == 'Buy':
                    mk = Market_Order_Execution()
                    mk.market_order(ut.tick, ticker, 0.01, tm.resistence, ut.position_current_price, decision_signal, ut.VOLUME, ut.MAGIC)
            elif stloss != "tail":
                if not mt5.positions_total() and decision_signal == 'Sell':
                    mk = Market_Order_Execution()
                    mk.market_order(ut.tick, ticker, stloss, tm.support, ut.position_current_price, decision_signal, ut.VOLUME, ut.MAGIC)
                if not mt5.positions_total() and decision_signal == 'Buy':
                    mk = Market_Order_Execution()
                    mk.market_order(ut.tick, ticker, stloss, tm.resistence, ut.position_current_price, decision_signal, ut.VOLUME, ut.MAGIC)
        
        elif auto_trade and full_list:

            ut.get_exposure(ticker)
            if stloss == "tail":
                tls = Tailing_Stoploss()
                tls.modify_position_tailling(sup=tm.support, resis=tm.resistence, tailling_value = 0.01)
                if mt5.positions_get(symbol=ticker) == () and decision_signal != 'Flat':
                    mk = Market_Order_Execution()
                    mk.market_order(ut.tick, ticker, 0.01, ut.position_current_price, decision_signal, ut.VOLUME, ut.MAGIC)
            elif stloss != "tail":
                if mt5.positions_get(symbol=ticker) == () and decision_signal != 'Flat':
                    mk = Market_Order_Execution()
                    mk.market_order(ut.tick, ticker, stloss, ut.position_current_price, decision_signal, ut.VOLUME, ut.MAGIC)
        
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
                        best_params_top = Params_Optimization(tickers_to_process, market_type, timeframe).best_params   

                        for _, row in best_params_top.iterrows():
                            utils_instance = Utils(row['Ticker'], market_type, timeframe)
                            self.main(ut=utils_instance, auto_trade=True, full_list=True, ticker=row['Ticker'], params=row)
                
                elif autotrade_set == 'off': 
                    while stop == False:
                        tickers = mt5.symbols_get()
                        tickers = pd.DataFrame(
                                    [[symbol.name, symbol.description, f"{symbol.currency_base}/{symbol.currency_profit}"] for symbol in tickers],
                                    columns=['Ticker', 'Description', 'Currency']
                                    ) 
                        
                        tickers_to_process = tickers['Ticker'].head(4).tolist()
                        best_params_top = Params_Optimization(tickers_to_process, market_type, timeframe).best_params   

                        for _, row in best_params_top.iterrows():
                            utils_instance = Utils(row['Ticker'], market_type, timeframe)
                            self.main(ut=utils_instance, auto_trade=False, full_list=False, ticker=row['Ticker'], params=row)
            
            elif ticker == 'Crypto':
                crypto = pd.DataFrame([[symbol.name, symbol.path] for symbol in mt5.symbols_get()], columns = ['Ticker', 'Path'])
                crypto = crypto[crypto['Path'].str.contains("crypto", case=False)]
                tickers_to_process = crypto['Ticker'].tolist()

                best_params_top = Params_Optimization(tickers_to_process, market_type, timeframe).best_params  

                for _, row in best_params_top.iterrows():
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
