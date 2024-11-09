'''
This file compile all the metrics used for trend measure
'''
import numpy as np
import pandas as pd
import pandas_ta as pta
from scipy import stats
from scipy.signal import find_peaks

class Trend_Metrics():
    
    def __init__(self) -> None:
                    
        self.result_df = pd.DataFrame(columns=['Function', 'Signal'])
        
        # get_crossover
        self.crossover_signal = None
        
        # get_sma_bands
        self.lower_band = None
        self.upper_band = None
        self.bbands_signal = None
        
        # get_rsi
        self.rsi_now = None
        self.rsi_signal = None

        # get_volume_profile
        self.support = None
        self.resistence = None
    
    def get_crossover(self, data : pd.DataFrame, l1: int, l2: int, l3: int):
        '''
        This function measures the crossover of 3 EMAs.
        
        Fundamental:
            * As long as the price remains above the chosen EMA level, the trader remains on the buy side, 
            if the price falls below the level of the selected EMA, the trader is a seller unless the price 
            crosses to the upside of the EMA.
            * When SMAs crossover between themself the result is in the conditions
            * 48% Success Rate
        
        Conditions:
            * Buy = ema1 > ema2 > ema3
            * Sell = ema1 < ema2 < ema3
            * Flat = Else
        '''
   
        # EMA1 
        self.ema_1 = pta.ema(data.close, length=l1).iloc[-1]
        ema_1_prev = pta.ema(data.close, length=l1).iloc[-2]
        # EMA2    
        self.ema_2 = pta.ema(data.close, length=l2).iloc[-1]
        ema_2_prev = pta.ema(data.close, length=l2).iloc[-2]
        # EMA3
        self.ema_3 = pta.ema(data.close, length=l3).iloc[-1]
        ema_3_prev = pta.ema(data.close, length=l3).iloc[-2]

        # Previous Cross Over Check
        if ema_1_prev > ema_2_prev > ema_3_prev:
            prev_signal = 'Buy' 
        elif ema_1_prev < ema_2_prev < ema_3_prev :
            prev_signal = 'Sell'
        else:
            prev_signal = 'Flat'
            
        # Current condition to mark signal
        if (prev_signal == 'Flat' or prev_signal == 'Sell') and ema_1_prev > ema_2_prev > ema_3_prev :
            self.crossover_signal = 'Buy'
        elif (prev_signal == 'Flat' or prev_signal == 'Buy') and ema_1_prev < ema_2_prev < ema_3_prev :
            self.crossover_signal = 'Sell'
        else:
            self.crossover_signal = 'Flat'

        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                                    'Function': ['Crossover'],
                                                                    'Signal': [self.crossover_signal]
                                                                })], ignore_index=True)

    def get_sma_bands(self, data : pd.DataFrame, l1 : int, std : int):
        '''
        This function measures the SMA Bollinger Bands interval
        
        Fundamental:
            * Bollinger Bands are envelopes plotted at a standard deviation level above and below a simple 
            moving average of the price. Because the distance of the bands is based on standard deviation,
            they adjust to volatility swings in the underlying price.
            * Identify sharp, short-term price movements and potential entry and exit points.
            * Bollinger Bands are able to capture about 90% of the price action in a given asset or cryptocurrency.
            * 95% Success Rate
            * Period = 14
            * Standard Deviation = 2
            
        Conditions:
            * Buy = Last Close Price <= Lower Band
            * Sell = Last Close Price >= Upper Band
            * Flat = Else  
        '''

        # Daily View
        data_bb = pta.bbands(data.close, length=l1, std=std)
        data_bb = data.join(data_bb)

        # Last close_price
        last_close_price = data_bb.iloc[-1].close
        self.lower_band = data_bb['BBL_{}_{}.0'.format(l1, std)].iloc[-1]
        self.upper_band = data_bb['BBU_{}_{}.0'.format(l1, std)].iloc[-1]
        
        # Finding signal
        if last_close_price < self.lower_band:
            self.bbands_signal = 'Buy'
        elif last_close_price > self.upper_band:
            self.bbands_signal = 'Sell'
        else:
            self.bbands_signal = 'Flat'
         
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                            'Function': ['Bollinger_Bands'],
                                                            'Signal': [self.bbands_signal]
                                                        })], ignore_index=True) 
 
    def get_rsi(self, data : pd.DataFrame, l1 : int, oblvl : int, oslvl : int):
        '''
        This function measures the Relative Strenght Index canal

        Fundamental:
            * The relative strength index (RSI) is a momentum indicator used in technical analysis. 
            RSI measures the speed and magnitude of a security's recent price changes to evaluate
            overvalued or undervalued conditions in the price of that security.
            * 90% Success Rate
            * Period = 14
            * Overbought = 70%
            * Oversold = 30%
            * Range = Last 1000 Candles 

        Conditions:
            * Buy = RSI value <= OVERSOLD_LEVEL
            * Sell = RSI value >= OVERBOUGHT_LEVEL
            * Flat = Else   
        '''
        
        rsi = pta.rsi(data.close, length=l1)
        self.rsi_now = rsi.iloc[-1] 

        if self.rsi_now >= oblvl:
            self.rsi_signal = 'Sell'
        elif self.rsi_now <= oslvl:
            self.rsi_signal = 'Buy'
        else:
            self.rsi_signal = 'Flat'
            
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                                    'Function': ['RSI'],
                                                                    'Signal': [self.rsi_signal]
                                                                })], ignore_index=True) 

    def get_volume_profile(self, data):
        '''
        Fundamental:    
            * Fixed Range Volume Profile Indicator 
            * This volume profile tool lets you analyse how much tranding volume occured at a specific price level over specific period of times. 
            * FRVPI is different from volume, Volume shows how much volume was tranded in a day while Fixed Volume presents how much Volume was traded in a especific price in a Period.
            * The Fixed Range Volume Profile Indicators is one of the best available because you can use it on both long-term and short-term trades, 
            as the histogram that is overlaid on the chart signifies significant price levels based on the volume of trade. 
            This indicator helps reveal what is happening with the stock and how its price could evolve in the future.
            * This indicator is essential for understanding supply, demand, and overall liquidity of stocks.
            * Shows the volume of trades at a particular price level, helping to identify significant price levels
        
        Conditions:
            * Volume Profile uses the following types of volume:
            * trade volume - for stocks.
            * tick volume*  - for indices/forex and crypto cfd
            
            * Point of Control (POC) – The price level for the time period with the highest traded volume.

            * Profile High – The highest reached price level during the specified time period.

            * Profile Low – The lowest reached price level during the specified time period.

            * Value Area (VA) – The range of price levels in which the specified percentage of all volume was traded during the time period. Typically, this percentage is set to 70%, however, it is up to the trader’s discretion.

            * Value Area High (VAH) – The highest price level within the value area.

            * Value Area Low (VAL) – The lowest price level within the value area.
        
            * This approach aligns with the concept of a normal distribution where approximately 68.26% of data points fall within one standard deviation from the mean.
        '''
        current_close_value = data.tail(1).close.iloc[0]
        
        # Daily 
        kde_factor = .01
        num_samples = 500
        kde = stats.gaussian_kde(data.close, weights=data.volume, bw_method=kde_factor)
        xr = np.linspace(data.close.min(), data.close.max(),num_samples)
        kdy = kde(xr)

        # Find Peaks of the distribution
        peaks, _ = find_peaks(kdy, prominence=1)

        close_avg_peak = xr[peaks]
        volume_pd_peak = kdy[peaks]
        
        peak_df = pd.DataFrame({'close_avg': close_avg_peak, 'volume_prob_d': volume_pd_peak})

        peak_df['dif_rate'] = current_close_value - peak_df['close_avg']

        self.support = peak_df[peak_df['dif_rate'] > 0].close_avg.max() 
        self.resistence = peak_df[peak_df['dif_rate'] < 0].close_avg.min() 

        peak_df = peak_df.sort_values(by='close_avg', ascending=True)
        peak_df.reset_index(inplace=True, drop=True)

        peak_df['peakvall_order'] = peak_df['close_avg'].rank(method='first')
        peak_df['poc_order'] = peak_df['volume_prob_d'].rank(method='first', ascending=False)




