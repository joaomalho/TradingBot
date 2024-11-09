'''
This file is responsible for metric variables evaluation 
'''

import itertools
import numpy as np
import pandas as pd
import datetime as dt
from Utils import Utils
import pandas_ta as pta
from tqdm import tqdm


class Params_Optimization():
    def __init__(self, ticker, market_type, timeframe) -> None:
        
        self.best_params = pd.DataFrame()

        best_params_rsi = pd.DataFrame({"Ticker": ticker,
                                        'Rsi_overbought': 70,
                                        'Rsi_oversold': 30,
                                    }, index=[0])
        
        if isinstance(ticker, list):
            for i in ticker:
                self.data = Utils(i, market_type, timeframe).data
                
                best_params_crossover = self.optimize_ema_crossover_strategy(self.data, i)
                best_params_bbans = self.optimize_sma_bands_strategy(self.data, i)
                
                df_crossover = best_params_crossover.to_frame().T
                df_bbans = best_params_bbans.to_frame().T

                self.best_params = pd.merge(pd.merge(df_crossover, df_bbans, on="Ticker"), best_params_rsi, on = "Ticker")

        elif isinstance(ticker, str): 
            self.data = Utils(ticker, market_type, timeframe).data
            
            best_params_crossover = self.optimize_ema_crossover_strategy(self.data, ticker)
            best_params_bbans = self.optimize_sma_bands_strategy(self.data, ticker)

            df_crossover = best_params_crossover.to_frame().T
            df_bbans = best_params_bbans.to_frame().T

            self.best_params = pd.merge(pd.merge(df_crossover, df_bbans, on="Ticker"), best_params_rsi, on = "Ticker")
     
    def optimize_ema_crossover_strategy(self, data, ticker):
        '''
        This function measures the optimization of Crossover strategy parameters
        '''
        # Combination for test
        ema1 = [10, 15, 20]
        ema2 = [25, 30, 50]
        ema3 = [100, 150, 200]

        # Optimization Params
        optimizer = 'Expectancy'

        combinations = list(itertools.product(ema1, ema2, ema3))
        simulation_results = []

        # Using itertools.product to generate all possible combinations
        for l1, l2, l3 in tqdm(combinations, desc="Optimizing EMA Crossover Strategy"):
            data['ema1'] = pta.ema(data.close, length=l1)
            data['ema2'] = pta.ema(data.close, length=l2)
            data['ema3'] = pta.ema(data.close, length=l3)
            data['returns_pips'] = (data['close'] - data['close'].shift(1))
            
            data['balance_crossover'] = 0.0 
            data['returns_pips_crossover'] = None
            data['crossover_signal'] = 0
            data['crossover_position_open'] = None
            data['crossover_position_close'] = None
            data['crossover_trade_number'] = None

            # Conditions of signal result by strategy
            open_pos_buy = False
            open_pos_sell = False
            trade_count = 0
            risk_free_rate = 0.025 

            for i, row in data.iterrows():
                if row['ema1'] > row['ema2'] > row['ema3']:
                    if not open_pos_buy:  
                        open_pos_buy = True
                        open_pos_sell = False
                        trade_count += 1  # Increment trade count
                        data.at[i, 'crossover_signal'] = 1
                        data.at[i, 'crossover_position_open'] = 1
                        data.at[i, 'crossover_trade_number'] = trade_count  # Assign trade number
                        data.at[i, 'returns_pips_crossover'] = data.at[i, 'returns_pips']
                        data.at[i, 'balance_crossover'] = data.at[i-1, 'balance_crossover'] + (data.at[i, 'returns_pips'] * 1 * 2)
                    else:
                        data.at[i, 'crossover_signal'] = 1
                        data.at[i, 'crossover_trade_number'] = trade_count
                        data.at[i, 'returns_pips_crossover'] = data.at[i, 'returns_pips']
                        data.at[i, 'balance_crossover'] = data.at[i-1, 'balance_crossover']
                elif row['ema1'] < row['ema2'] < row['ema3']:
                    if not open_pos_sell:
                        open_pos_buy = False
                        open_pos_sell = True
                        trade_count += 1  # Increment trade count
                        data.at[i, 'crossover_position_open'] = -1
                        data.at[i, 'crossover_signal'] = -1
                        data.at[i, 'crossover_trade_number'] = trade_count  # Assign trade number
                        data.at[i, 'returns_pips_crossover'] = -data.at[i, 'returns_pips']
                        data.at[i, 'balance_crossover'] = data.at[i-1, 'balance_crossover'] -(data.at[i, 'returns_pips'] * 1 * 2)
                    else:
                        data.at[i, 'crossover_signal'] = -1
                        data.at[i, 'returns_pips_crossover'] = -data.at[i, 'returns_pips']
                        data.at[i, 'crossover_trade_number'] = trade_count
                        data.at[i, 'balance_crossover'] = data.at[i-1, 'balance_crossover']
                elif open_pos_buy:
                    open_pos_buy = False
                    data.at[i, 'crossover_position_close'] = 1
                    data.at[i, 'balance_crossover'] = data.at[i-1, 'balance_crossover']
                elif open_pos_sell:
                    open_pos_sell = False
                    data.at[i, 'crossover_position_close'] = -1
                    data.at[i, 'balance_crossover'] = data.at[i-1, 'balance_crossover']

            # Reporting
            total_buy_op = (data.groupby('crossover_trade_number')['crossover_signal'].sum() > 0).sum()
            total_sell_op = (data.groupby('crossover_trade_number')['crossover_signal'].sum() < 0).sum()
            total_op = total_buy_op+total_sell_op
            total_win_op = (data.groupby('crossover_trade_number')['returns_pips_crossover'].sum() > 0).sum()
            total_lost_op = (data.groupby('crossover_trade_number')['returns_pips_crossover'].sum() < 0).sum()
            total_win_op_pips = data[data['returns_pips_crossover'] > 0].groupby('crossover_trade_number')['returns_pips_crossover'].sum().sum()
            total_lost_op_pips = data[data['returns_pips_crossover'] < 0].groupby('crossover_trade_number')['returns_pips_crossover'].sum().sum()
            sortino_ratio = ((data[data['returns_pips_crossover']!=0].groupby('crossover_trade_number')['returns_pips_crossover'].sum().mean()) - risk_free_rate) / (np.sqrt((((data[data['returns_pips_crossover'] < 0].groupby('crossover_trade_number')['returns_pips_crossover'].sum()) - (-2.5))**2).mean()))
            if total_op != 0:
                win_rate = round((total_win_op / total_op) * 100, 2)
            else:
                win_rate = 0
            loss_rate = 100 - win_rate
            if total_win_op != 0 and total_lost_op != 0:
                riskreward = (total_win_op_pips / total_win_op) / (-1 * total_lost_op_pips / total_lost_op)
            else:
                riskreward = 0
            if total_win_op != 0 and total_lost_op != 0:
                avg_win = total_win_op_pips / total_win_op
                avg_loss = total_lost_op_pips / total_lost_op
                expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
            else:
                avg_win = 0
                avg_loss = 0
                expectancy = 0

            best_params = pd.DataFrame({'Ticker' : [ticker],
                                        'Optimizer_Cross' : [optimizer],
                                        'WinRate_Cross' : [win_rate],
                                        'Sortino_Cross' : [sortino_ratio],
                                        'Riskreward_Cross' : [riskreward],
                                        'Expectancy_Cross' : [expectancy],
                                        'Best_Ema1_Cross': [l1],
                                        'Best_Ema2_Cross': [l2],
                                        'Best_Ema3_Cross': [l3],
                                    }, index=[0])

            simulation_results.append(best_params)

        simulation_results_df = pd.concat(simulation_results, ignore_index=True)
        self.best_params_crossover = simulation_results_df.iloc[simulation_results_df['Expectancy_Cross'].idxmax()]
        return self.best_params_crossover

    def optimize_sma_bands_strategy(self, data, ticker):
        '''
        This function measures the optimization of Bollinger Bands strategy parameters
        '''
        # Combination for test
        ema = [10, 12, 15, 20, 25]
        std_list = [1, 2, 3]

        # Optimization Params
        optimizer = 'Expectancy'
        
        combinations = list(itertools.product(ema, std_list))
        simulation_results = []

        for l1, std in tqdm(combinations, desc="Optimizing Bollinger Bands Strategy"):

            data_bands = pta.bbands(data.close, length=l1, std=std)
        
            data = data.join(data_bands)

            data.rename(columns={data.filter(like='BBU').columns[0]: 'bb_upperband'+str(l1)+str(std)}, inplace=True)
            data.rename(columns={data.filter(like='BBL').columns[0]: 'bb_lowerband'+str(l1)+str(std)}, inplace=True)
            data.rename(columns={data.filter(like='BBM').columns[0]: 'bb_middleband'+str(l1)+str(std)}, inplace=True)

            data['returns_pips'] = (data['close'] - data['close'].shift(1))
            data['balance_bbands'] = 0.0
            data['returns_pips_bbands'] = None
            data['bbands_signal'] = 0
            data['bbands_signal_positions'] = None
            data['bbands_signal_positions_close'] = None
            data['bbands_position_open'] = None
            data['bbands_position_close'] = None
            data['bbands_trade_number'] = None

            # Conditions of signal result by strategy
            open_pos_buy = False
            open_pos_sell = False 
            trade_count = 0
            risk_free_rate = 0.025 

            for i, row in data.iterrows():
                if row['bb_lowerband'+str(l1)+str(std)] > row['close']:
                    if not open_pos_buy:
                        open_pos_buy = True
                        open_pos_sell = False
                        trade_count += 1  # Increment trade count
                        data.at[i, 'bbands_signal'] = 1
                        data.at[i, 'bbands_position_open'] = 1
                        data.at[i, 'bbands_position_close'] = -1
                        data.at[i, 'bbands_trade_number'] = trade_count  # Assign trade number
                        data.at[i, 'returns_pips_bbands'] = data.at[i, 'returns_pips']
                        if i > 0:
                            data.at[i, 'balance_bbands'] = data.at[i-1, 'balance_bbands'] + data.at[i, 'returns_pips'] * 1 * 2
                    else:
                        data.at[i, 'bbands_signal'] = 1
                        data.at[i, 'bbands_trade_number'] = trade_count
                        data.at[i, 'returns_pips_bbands'] = data.at[i, 'returns_pips']
                        if i > 0:
                            data.at[i, 'balance_bbands'] = data.at[i-1, 'balance_bbands']
                elif row['bb_upperband'+str(l1)+str(std)] < row['close']:
                    if not open_pos_sell:
                        open_pos_buy = False
                        open_pos_sell = True
                        trade_count += 1  # Increment trade count
                        data.at[i, 'bbands_signal'] = -1
                        data.at[i, 'bbands_position_open'] = -1
                        data.at[i, 'bbands_position_close'] = 1
                        data.at[i, 'bbands_trade_number'] = trade_count  # Assign trade number
                        data.at[i, 'returns_pips_bbands'] = -data.at[i, 'returns_pips']
                        if i > 0:
                            data.at[i, 'balance_bbands'] = data.at[i-1, 'balance_bbands'] - data.at[i, 'returns_pips'] * 1 * 2
                    else:
                        data.at[i, 'bbands_signal'] = -1
                        data.at[i, 'returns_pips_bbands'] = data.at[i, 'returns_pips']
                        data.at[i, 'bbands_trade_number'] = trade_count  # Assign trade number
                        if i > 0:
                            data.at[i, 'balance_bbands'] = data.at[i-1, 'balance_bbands']

            # Reporting
            total_buy_op = (data.groupby('bbands_trade_number')['bbands_signal'].sum() > 0).sum()
            total_sell_op = (data.groupby('bbands_trade_number')['bbands_signal'].sum() < 0).sum()
            total_op = total_buy_op+total_sell_op
            total_win_op = (data.groupby('bbands_trade_number')['returns_pips_bbands'].sum() > 0).sum()
            total_win_op_pips = data[data['returns_pips_bbands'] > 0].groupby('bbands_trade_number')['returns_pips_bbands'].sum().sum()
            total_lost_op = (data.groupby('bbands_trade_number')['returns_pips_bbands'].sum() < 0).sum()
            total_lost_op_pips = data[data['returns_pips_bbands'] < 0].groupby('bbands_trade_number')['returns_pips_bbands'].sum().sum()
            sortino_ratio = ((data[data['returns_pips_bbands']!=0].groupby('bbands_trade_number')['returns_pips_bbands'].sum().mean()) - risk_free_rate) / (np.sqrt((((data[data['returns_pips_bbands'] < 0].groupby('bbands_trade_number')['returns_pips_bbands'].sum()) - (-2.5))**2).mean()))
            if total_op != 0:
                win_rate = round((total_win_op / total_op) * 100, 2)
            else:
                win_rate = 0
            loss_rate = 100 - win_rate
            if total_win_op != 0 and total_lost_op != 0:
                riskreward = (total_win_op_pips / total_win_op) / (-1 * total_lost_op_pips / total_lost_op)
            else:
                riskreward = 0
            if total_win_op != 0 and total_lost_op != 0:
                avg_win = total_win_op_pips / total_win_op
                avg_loss = total_lost_op_pips / total_lost_op
                expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
            else:
                avg_win = 0
                avg_loss = 0
                expectancy = 0
            
            best_params = pd.DataFrame({'Ticker' : [ticker],
                                        'Optimizer_Bbands' : [optimizer],
                                        'WinRate_Bbands' : [win_rate],
                                        'Sortino_Bbands' : [sortino_ratio],
                                        'Riskreward_Bbands' : [riskreward],
                                        'Expectancy_Bbands' : [expectancy],
                                        'Best_Ema1_Bbands': [l1],
                                        'Best_std_Bbands': [std],
                                        }, index=[0])

            simulation_results.append(best_params)

        simulation_results_df = pd.concat(simulation_results, ignore_index=True)
        self.best_params_bbans = simulation_results_df.iloc[simulation_results_df['Expectancy_Bbands'].idxmax()]
        return self.best_params_bbans
            

       

