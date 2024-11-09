'''
This file regards all support and resistences detection
'''

import pandas as pd

class Support_Resistences():
    '''
    This class regard several Support and Resistences measures
    '''
    def __init__(self) -> None:
        
        self.result_df = pd.DataFrame(columns=['Function', 'Signal', 'Relevance'])
        
        self.daily_last_support = None
        self.daily_last_resistence = None
        self.daily_sup_resis_signal = None 
        self.daily_sup_resis_signal_relevance = None
        
    def get_sup_resis_fractal(self, daily_data, current_price):
        '''
        This function measures the existence of Support and Resistences
        
        Fundamental:
            * The support and resistance (S&R) are specific price points on a chart expected to attract the maximum amount of either 
            buying or selling. 
            * Support - Is a price at which one can expect more buyers than sellers. 
            * Resistance - Is a price at which one can expect more sellers than buyers.
        
        Conditions:
            * Buy = Support
            * Sell = Resistnece
            * Flat = Else     
        '''

        # Daily View
        daily_bars_supresis_df = daily_data 
        
        # Daily View
        def isSupport_5candles(df,i):
            support = df['low'][i] < df['low'][i-1] \
                        and df['low'][i] < df['low'][i+1] \
                        and df['low'][i+1] < df['low'][i+2] \
                        and df['low'][i-1] < df['low'][i-2]
            return support
        def isResistance_5candles(df,i):
            resistance = df['high'][i] > df['high'][i-1] \
                        and df['high'][i] > df['high'][i+1] \
                        and df['high'][i+1] > df['high'][i+2] \
                        and df['high'][i-1] > df['high'][i-2]
            return resistance

        daily_levels_5candles = []
        for i in range(2,daily_bars_supresis_df.shape[0]-2):
            if isSupport_5candles(daily_bars_supresis_df,i):
                daily_levels_5candles.append((i,daily_bars_supresis_df['low'][i],'support'))
            elif isResistance_5candles(daily_bars_supresis_df,i):
                daily_levels_5candles.append((i,daily_bars_supresis_df['high'][i],'resistence'))
        
        daily_levels_5candles_df = pd.DataFrame(daily_levels_5candles)
        daily_levels_5candles_df.rename(columns={0:'level_position',
                                        1:'level_value',
                                        2:'level_type'},
                            inplace=True
                            )
            
        daily_levels_5candles_df_supports = daily_levels_5candles_df[daily_levels_5candles_df['level_type'] == 'support']
        daily_last_support = daily_levels_5candles_df_supports.iloc[-1].level_value # 110	987	1.06200	support

        daily_levels_5candles_df_resistences = daily_levels_5candles_df[daily_levels_5candles_df['level_type'] == 'resistence']
        daily_last_resistence = daily_levels_5candles_df_resistences.iloc[-1].level_value  # 111	993	1.06387	resistence
        
        if daily_levels_5candles_df.iloc[-1, 2] == 'resistence' and (current_price < daily_levels_5candles_df.iloc[-1, 1]): # we should measure the distance of resistence until price, and if it is close then surpass the resistence 
            daily_sup_resis_signal = 'Sell'
            daily_sup_resis_signal_relevance = 20
        elif daily_levels_5candles_df.iloc[-1, 2] == 'support' and (current_price > daily_levels_5candles_df.iloc[-1, 1]):
            daily_sup_resis_signal = 'Buy'
            daily_sup_resis_signal_relevance = 20
        else: 
            daily_sup_resis_signal = 'Flat'
            daily_sup_resis_signal_relevance = 0
        
        self.daily_last_support = daily_last_support
        self.daily_last_resistence = daily_last_resistence
        self.daily_sup_resis_signal = daily_sup_resis_signal
        self.daily_sup_resis_signal_relevance = daily_sup_resis_signal_relevance
        
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                    'Function': ['Support or Resistence'],
                                                    'Signal': [self.daily_sup_resis_signal],
                                                    'Relevance': [self.daily_sup_resis_signal_relevance]
                                                })], ignore_index=True) 
