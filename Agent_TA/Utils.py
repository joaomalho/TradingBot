'''
    This file is responsible to organize and detail all the Variables across the grid 
'''

# Python Libraries
import numpy as np
import pandas as pd
import datetime as dt
import MetaTrader5 as mt5
from datetime import time
from connections import Connections

class Utils():
    def __init__(self, ticker, market_type, timeframe) -> None:
        #============= FIXED VARIAVEIS =============#
            # Strategy parameters
        self.SYMBOL = ticker #'EURUSD'        
        self.MAGIC = 100 # Ref
        self.VOLUME = 0.02 # Size of lot
        self.START_POSITION = 0
        self.NUMBER_BARS = 1000

        # VOLATILITY FUNCTIONS
            # SMA Bands parameters      
        self.SMA_PERIOD = 14 # SMA 14
        self.STANDARD_DEVIATION_SMA = 2 # Deviation of 2
            # RSI parameters
        self.RSI_PERIOD = 14
        self.OVERBOUGHT_LEVEL = 70
        self.OVERSOLD_LEVEL = 30
        self.MIDDLE_LEVEL = 50
                # Harmonic Patterns
        self.err_allowed = 10.0/100 
        
        # ============= Data =============#
    
        if market_type == 'Cambial':
            if timeframe == "15M":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_M15, self.START_POSITION, 1000))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
            
            if timeframe == "30M":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_M30, self.START_POSITION, 1000))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
                
            if timeframe == "1H":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_H1, self.START_POSITION, 1000))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
                
            if timeframe == "4H":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_H4, self.START_POSITION, 1000))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
 
            if timeframe == "1D":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_D1, self.START_POSITION, 1000))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
                
            self.data.rename(columns={'tick_volume': 'volume'}, inplace=True)

            self.daily_tuning = self.data[['time', 'open', 'high', 'low', 'close']].copy()
            self.daily_tuning.rename(columns={'time': "Time", 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
            self.daily_tuning.set_index('Time', inplace=True)
            
            self.tick = mt5.symbol_info_tick(self.SYMBOL)            
            self.position_current_price = self.tick[1]


        self.exposure = self.get_exposure(self.SYMBOL)
        
        # Define market session times for a hypothetical market
        self.market_sessions = {
                'Sydney': (time(21, 0), time(23, 59)),
                'Sydney_Tokyo': (time(0, 0), time(5, 59)),
                'Tokyo': (time(6, 0), time(6, 59)),
                'Tokyo_London': (time(7, 0), time(8, 59)),
                'London': (time(9, 0), time(11, 59)),
                'London-NYork': (time(12, 0), time(15, 59)),
                'NYork': (time(16, 0), time(20, 59))
            }

        # # Get the current time
        self.current_time = dt.datetime.now().time()
        # for session, (open_time, close_time) in self.market_sessions.items():
        #     if open_time <= current_time <= close_time:
        #         current_session = session
        #         pass
        # if current_session:
        #     self.current_session = current_session
        # else:
        #     self.current_session = 'Market Closed'

        #============= Market Order Execution Data =============#
        #============= INFORMATION PART =============#
        # Admin Info
        self.result_df = pd.DataFrame(columns=['Date',
                                                'Ticker',
                                                # 'Session', 
                                                'Magic', 
                                                'Exposure', 
                                                'CurrentPrice',
                                                'SMAPeriod',
                                                'SMAStandardDeviation',
                                                'CandlesRange',
                                                'RSIPeriod',
                                                'RSIOverbought',
                                                'RSIOversold',
                                                'RSIMiddle'
                                                ])

        non_empty_columns = self.result_df.columns[~self.result_df.isna().all()]
        if self.result_df.empty or self.result_df[non_empty_columns].isna().all().all():
            new_data = pd.DataFrame({
                                        'Date': [self.current_time],
                                        'Ticker': [self.SYMBOL],
                                        # 'Session': [self.current_session],
                                        'Magic': [self.MAGIC],
                                        'Exposure': [self.exposure],
                                        'CurrentPrice': [self.position_current_price],
                                        'SMAPeriod': [self.SMA_PERIOD],
                                        'SMAStandardDeviation': [self.STANDARD_DEVIATION_SMA],
                                        'CandlesRange': [self.NUMBER_BARS],
                                        'RSIPeriod': [self.RSI_PERIOD],
                                        'RSIOverbought': [self.OVERBOUGHT_LEVEL],
                                        'RSIOversold': [self.OVERSOLD_LEVEL],
                                        'RSIMiddle': [self.MIDDLE_LEVEL],
                                    })
            self.result_df = pd.concat([self.result_df, new_data], ignore_index=True)
        else:
            new_data = pd.DataFrame({
                                        'Date': [dt.datetime.now()],
                                        'Ticker': [self.SYMBOL],
                                        # 'Session': [self.current_session],
                                        'Magic': [self.MAGIC],
                                        'Exposure': [self.exposure],
                                        'CurrentPrice': [self.position_current_price],
                                        'SMAPeriod': [self.SMA_PERIOD],
                                        'SMAStandardDeviation': [self.STANDARD_DEVIATION_SMA],
                                        'CandlesRange': [self.NUMBER_BARS],
                                        'RSIPeriod': [self.RSI_PERIOD],
                                        'RSIOverbought': [self.OVERBOUGHT_LEVEL],
                                        'RSIOversold': [self.OVERSOLD_LEVEL],
                                        'RSIMiddle': [self.MIDDLE_LEVEL],
                                    })
            self.result_df = pd.concat([self.result_df, new_data], ignore_index=True)
    
        # == Store Settings == #
        # Connections().sql_connect(table_db_name='settings', table=self.result_df, ifexists='append')

    # ======= INFORMATION PART ======= #
    
    def get_exposure(self, symbol):
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            pos_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())
            exposure = pos_df['volume'].sum()
        else:
            exposure = self.VOLUME
        return exposure    
    
    def login():
        # User credentials
        # Log in to the server account of MT5
        mt5.initialize()
        mt5.login(52023326, '1d8@Mo50i9n6oU', 'ICMarketsSC-Demo')
        





    def get_tickerlist(self):
        tickerlists = pd.DataFrame([[symbol.name, symbol.path, symbol.description] for symbol in mt5.symbols_get()], columns = ['Ticker', 'Path', 'Description'])

        tickerlists['type'] = np.where(tickerlists['Path'].str.contains("forex", case=False), 'cambial',
                                    np.where(tickerlists['Path'].str.contains("crypto", case=False), 'crypto',
                                                np.where(tickerlists['Path'].str.contains("indices", case=False), 'indice',
                                                        np.where(tickerlists['Path'].str.contains("commodities", case=False), 'commodity',
                                                                np.where(tickerlists['Path'].str.contains("stock", case=False), 'stock', None)
                                                                )
                                                        )
                                            )
                                    )
        self.tickerlists = tickerlists










# Setting for prints
class Config():
    def __init__(self) -> None:
            
        self.PURPLE = '\033[95m'
        self.CYAN = '\033[96m'
        self.DARKCYAN = '\033[36m'
        self.BLUE = '\033[94m'
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.RED = '\033[91m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'
        self.END = '\033[0m'