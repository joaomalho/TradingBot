'''
This file is responsible for metric variables evaluation 
'''

import numpy as np
import pandas as pd
import datetime as dt
from Utils import Utils
import pandas_ta as pta
from connections import Connections
from backtesting import Strategy, Backtest


class Params_Optimization():
    def __init__(self, ticker, market_type, timeframe) -> None:
        self.best_params = pd.DataFrame()
        
        if isinstance(ticker, list):
            for i in ticker:
                self.tuning_data = Utils(i, market_type, timeframe).daily_tuning
                
                self.best_params_crossover = self.optimize_ema_crossover_strategy(self.tuning_data, i)
                self.best_params_bbans = self.optimize_sma_bands_strategy(self.tuning_data, i)
                self.best_params_rsi = self.optimize_rsi_strategy(self.tuning_data, i)
                
                self.best_params_full = pd.merge(pd.merge(self.best_params_crossover, self.best_params_bbans, on='Ticker'), self.best_params_rsi, on='Ticker')
                self.best_params = pd.concat([self.best_params, self.best_params_full], ignore_index=True)
                
                # Calculate the mean of Win Rate
                columns_to_average = ['OptimizerResult_Cross', 'OptimizerResult_Bbands', 'OptimizerResult_Rsi'] 
                self.best_params['WinRate_avg'] = self.best_params[columns_to_average].mean(axis=1)

                # Connections().sql_connect(table_db_name='best_parameters', table=self.best_params, ifexists='append')
        
        elif isinstance(ticker, str): 
            self.tuning_data = Utils(ticker, market_type, timeframe).daily_tuning
            
            self.best_params_crossover = self.optimize_ema_crossover_strategy(self.tuning_data, ticker)
            self.best_params_bbans = self.optimize_sma_bands_strategy(self.tuning_data, ticker)
            self.best_params_rsi = self.optimize_rsi_strategy(self.tuning_data, ticker)
            
            self.best_params_full = pd.merge(pd.merge(self.best_params_crossover, self.best_params_bbans, on='Ticker'), self.best_params_rsi, on='Ticker')
            self.best_params = pd.concat([self.best_params, self.best_params_full], ignore_index=True)
            
            # Calculate the mean of Win Rate
            columns_to_average = ['OptimizerResult_Cross', 'OptimizerResult_Bbands', 'OptimizerResult_Rsi'] 
            self.best_params['WinRate_avg'] = self.best_params[columns_to_average].mean(axis=1)

            # Connections().sql_connect(table_db_name='best_parameters', table=self.best_params, ifexists='append')

    def optimize_ema_crossover_strategy(self, tuning_data, ticker):
        class MyCrossoverStrat(Strategy):
            FirstEma = 13
            SecondEma = 48
            ThirdEma = 200

            def init(self):
                self.ema13 = self.I(pta.ema, tuning_data.Close, self.FirstEma)
                self.ema48 = self.I(pta.ema, tuning_data.Close, self.SecondEma)
                self.ema200 = self.I(pta.ema, tuning_data.Close, self.ThirdEma)

            def next(self):
                if (self.ema13 < self.ema48 < self.ema200):
                    if self.position.is_long or not self.position:
                        self.position.close()
                        self.sell(size=1)

                elif self.ema13 > self.ema48 > self.ema200:
                    if self.position.is_short or not self.position:
                        self.position.close()
                        self.buy(size=1)

        tuning_bt = Backtest(data=tuning_data, strategy=MyCrossoverStrat, cash=200_000, commission=0.00, exclusive_orders=True)
        print('OPTIMIZING EMA Crossovers METRICS...')

        # Optimization Params
        optimizer = 'Win Rate [%]'

        stats = tuning_bt.optimize(
            FirstEma = range(5, 25, 1),
            SecondEma = range(26, 80, 1),
            ThirdEma = range(81, 200, 1),
            maximize = optimizer,
            max_tries = 200
        )
        self.best_params_ema_crossover = pd.DataFrame({'Date' : [dt.datetime.now()],
                                        'Ticker' : [ticker],
                                        'Optimizer' : [optimizer],
                                        'OptimizerResult_Cross' : [stats[optimizer]],
                                        'BEST_FIRST_PERIOD_Ema_Cross': [stats._strategy.FirstEma],
                                        'BEST_SECOND_PERIOD_Ema_Cross': [stats._strategy.SecondEma],
                                        'BEST_THIRD_PERIOD_Ema_Cross': [stats._strategy.ThirdEma],
                                    }, index=[0])

        return self.best_params_ema_crossover

    def optimize_sma_bands_strategy(self, tuning_data, ticker):
        class MyBandsStrat(Strategy):
            Length = 14
            Std = 2

            def init(self):
                # Calculate Bollinger Bands
                self.bbands_data = self.I(pta.bbands, tuning_data.Close, self.Length, self.Std)
                
                # Check if the array is not empty or contains only NaN values
                if np.any(~np.isnan(self.bbands_data[:, 3])):
                    self.bbb_col_mean = np.nanmean(self.bbands_data[:, 3])
                else:
                    self.bbb_col_mean = np.nan  # Set mean to NaN if the array is empty or contains only NaN values

            def next(self):
                # Check if the array is not empty or contains only NaN values
                if np.any(~np.isnan(self.bbands_data[:, 3])):
                    if self.bbands_data[:, 3] > self.bbb_col_mean:
                        if self.data.Close < self.bbands_data[:, 0]:
                            self.position.close()
                            self.buy(size=1)  # Buy
                        elif self.data.Close > self.bbands_data[:, 2]:
                            self.position.close()
                            self.sell(size=1)  # Sell

        tuning_bt = Backtest(data=tuning_data, strategy=MyBandsStrat, cash=200_000, commission=0.00, exclusive_orders=True)
        print('OPTIMIZING Bollinger Bands METRIC...')
        
        # Optimization Params
        optimizer = 'Win Rate [%]'

        stats = tuning_bt.optimize(
            Length = range(8, 25, 1),
            Std = range(1, 10, 1),
            maximize= optimizer, #optimizer_params,
            max_tries=200
        )

        self.best_params_bbands = pd.DataFrame({'Date' : [dt.datetime.now()],
                                        'Ticker' : [ticker],
                                        'Optimizer' : [optimizer],
                                        'OptimizerResult_Bbands' : [stats[optimizer]],
                                        'BEST_LENGHT_Bbands' : [stats._strategy.Length],
                                        'BEST_STD_Bbands' : [stats._strategy.Std],
                                    }, index=[0])

        return self.best_params_bbands

    def optimize_rsi_strategy(self, tuning_data, ticker):
        class MyRsiStrat(Strategy):
            Overbought_level = 70
            Oversold_level =  30
            Length = 2

            def init(self):
                # Calculate Bollinger Bands
                self.rsi = self.I(pta.rsi, tuning_data.Close, self.Length)
                
            def next(self):
                if self.rsi < self.Oversold_level:
                    if self.position.is_long or not self.position:
                        self.position.close()
                        self.buy(size=1)  # Buy
                elif self.rsi > self.Overbought_level:
                    if self.position.is_short or not self.position:
                        self.position.close()
                        self.sell(size=1)  # Sell

        def custom_optimizer_params(strategy):
            if strategy._strategy.Overbought_level + strategy._strategy.Oversold_level != 100:
                return -1

            return strategy['Win Rate [%]']

        tuning_bt = Backtest(data=tuning_data, strategy=MyRsiStrat, cash=200_000, commission=0.00, exclusive_orders=True)
        print('OPTIMIZING Rsi METRIC...')
        
        # Optimization Params
        optimizer = 'Win Rate [%]'

        stats = tuning_bt.optimize(
            Length = range(8, 20, 1),
            Overbought_level = range(60, 80, 5),
            Oversold_level = range(20, 40, 5),
            maximize=custom_optimizer_params,
            max_tries=200
        )

        self.best_params_rsi = pd.DataFrame({'Date' : [dt.datetime.now()],
                                        'Ticker' : [ticker],
                                        'Optimizer' : [optimizer],
                                        'OptimizerResult_Rsi' : [stats[optimizer]],
                                        'BEST_LENGHT_Rsi' : [stats._strategy.Length],
                                        'BEST_OVERBOUGHT_Rsi' : [stats._strategy.Overbought_level],
                                        'BEST_OVERSOLD_Rsi' : [stats._strategy.Oversold_level],
                                    }, index=[0])

        return self.best_params_rsi
    
       


### NA DECISÃO SÓ PODE ABRIR POSIÇÕES QUE TENHO AVG. WINRATE > 50 % REFORÇANDO A DECISÃO AUTOMATICA DO ALGORITMO.
 