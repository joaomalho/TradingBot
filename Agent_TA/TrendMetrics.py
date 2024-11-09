'''
This file compile all the metrics used for trend measure
'''
import pandas as pd
import pandas_ta as pta

class Trend_Metrics():
    
    def __init__(self) -> None:
                    
        self.result_df = pd.DataFrame(columns=['Function', 'Signal', 'Relevance'])
        
        # get_crossover
        self.ma_1 = None
        self.ma_2 = None 
        self.ma_3 = None
        self.crossover_trend = None
        self.crossover_signal = None
        self.crossover_relevance = None
        
        # get_sma_bands
        self.sd = None
        self.sma_period = None
        self.lower_band = None
        self.upper_band = None
        self.width_band = None
        self.last_close_price = None
        self.bbands_signal = None
        self.bbands_relevance = None
        
        # get_rsi
        self.rsi_now = None
        self.rsi_signal = None
        self.signal_rsi_relevance = None
        
        # Market Session
        self.current_session = None  
        
        # Combined EMAs & Bollinger Bands
        self.comb_bb_rsi_signal = None
        self.comb_bb_rsi_relevance = None

        # Volume PVI and NVI    
        self.pvi_signal = None
        self.pvi_now = None
        self.pvi_relevance = None
        self.nvi_signal = None
        self.nvi_now = None
        self.nvi_relevance = None
        
        # Macd
        self.macd_signal = None
        self.macd_EMA26 = None
        self.macd_EMA12 = None
        self.macd_Signal_Line = None
        self.macd_relevance = None
        
    # ========= TREND TECHNIQUES ========= #
    
    def get_crossover(self, data : pd.DataFrame, l1: int, l2: int, l3: int, type : bool = 1):
        '''
        This function measures the crossover of 3 EMAs.
        
        Fundamental:
            * As long as the price remains above the chosen EMA level, the trader remains on the buy side, 
            if the price falls below the level of the selected EMA, the trader is a seller unless the price 
            crosses to the upside of the EMA.
            * When SMAs crossover between themself the result is in the conditions
            * 48% Success Rate
        
        Conditions:
            * Buy = 13 > 48 > 200
            * Sell = 13 < 48 < 200
            * Flat = Else
        '''
   
        # EMA13 
        ema_1 = pta.ema(data.close, length=l1).iloc[-1]
        ema_1_prev = pta.ema(data.close, length=l1).iloc[-2]
        # EMA48    
        ema_2 = pta.ema(data.close, length=l2).iloc[-1]
        ema_2_prev = pta.ema(data.close, length=l2).iloc[-2]
        # EMA200
        ema_3 = pta.ema(data.close, length=l3).iloc[-1]
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
            emas_crossover_signal = 'Buy'
            emas_crossover_relevance = 48

        elif (prev_signal == 'Flat' or prev_signal == 'Buy') and ema_1_prev < ema_2_prev < ema_3_prev :
            emas_crossover_signal = 'Sell'
            emas_crossover_relevance = 48
        else:
            emas_crossover_signal = 'Flat'
            emas_crossover_relevance = 0

        self.crossover_signal = emas_crossover_signal
        self.ma_1 = ema_1   
        self.ma_2 = ema_2
        self.ma_3 = ema_3
        self.crossover_relevance = emas_crossover_relevance

        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                                    'Function': ['Crossover'],
                                                                    'Signal': [self.crossover_signal],
                                                                    'Relevance': [self.crossover_relevance]
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
        bbl_last = data_bb['BBL_{}_{}.0'.format(l1, std)].iloc[-1]
        bbu_last = data_bb['BBU_{}_{}.0'.format(l1, std)].iloc[-1]
        bbb_last = data_bb['BBB_{}_{}.0'.format(l1, std)].iloc[-1]
        bbb_mean = data_bb['BBB_{}_{}.0'.format(l1, std)].mean()

        # Finding signal
        if bbb_last > bbb_mean:
            if last_close_price < bbl_last:
                bb_signal = 'Buy'
                bb_relevance = 95
            elif last_close_price > bbu_last:
                bb_signal = 'Sell'
                bb_relevance = 95
            else:
                bb_signal = 'Flat'
                bb_relevance = 0
        else:
            bb_signal = 'Flat'
            bb_relevance = 0

        self.bbands_signal = bb_signal
        self.sd = std
        self.sma_period = l1
        self.lower_band = bbl_last
        self.upper_band = bbu_last
        self.width_band = bbb_last
        self.last_close_price = last_close_price
        self.bbands_relevance = bb_relevance
       
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                            'Function': ['Bollinger_Bands'],
                                                            'Signal': [self.bbands_signal],
                                                            'Relevance': [self.bbands_relevance]
                                                        })], ignore_index=True) 


    # ========= MOMENTUM TECHNIQUES ========= #  
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
        rsi_now = rsi.iloc[-1] 

        if rsi_now >= oblvl:
            rsi_signal = 'Sell'
            rsi_relevance = 90
        elif rsi_now <= oslvl:
            rsi_signal = 'Buy'
            rsi_relevance = 90
        else:
            rsi_signal = 'Flat'
            rsi_relevance = 0
            
        self.rsi_signal = rsi_signal
        self.rsi_now = rsi_now
        self.rsi_relevance = rsi_relevance

        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                                    'Function': ['RSI'],
                                                                    'Signal': [self.rsi_signal],
                                                                    'Relevance': [self.rsi_relevance]
                                                                })], ignore_index=True) 

    def get_macd(self, data : pd.DataFrame):
        '''
        Fundamental:
            * MACD is used to identify aspects of general trend, like detect impulse, diretion and trend duration
            * Firstly are used 2 EMAS one with 12 un. period and other with 26 un. period (which are delayed indicators), to identify the trend direction and duration.
            * Secondly the diference between previous EMAs (MACD Line) is calculated and applyed a EMA of 9 un. (Signal Line).
            * Tirdly the diference between MACD Line and Signal Line is ploted in a histogram that moves up and down of one Zero Line Central
            * The histogram is used as a good indicator of a stock dynamic 
            * MACD is good to identify 3 types of basic signals:
                * Signal Line Crossovers
                * Zero Line Crossovers
                * Divergence

        Conditions:
            * MACD Line: (EMA of 12 days – EMA of 26 days) 
            * Signal Line: EMA of 9 dias of MACD line
            * MACD Histogram: MACD Line - Signal Line

            __Signal Line Crossovers__
            
            ```python
            for i in range(1, len(data)):

                    if (data['macd_signal_line'].iloc[i-1] > data['macd_line'].iloc[i-1] 
                                and data['macd_signal_line'].iloc[i] <= data['macd_line'].iloc[i] 
                                and data['macd_signal_line'].iloc[i-1] < 0 
                                and data['macd_line'].iloc[i-1] < 0
                                and data['macd_signal_line'].iloc[i] < 0
                                and data['macd_line'].iloc[i] < 0 
                                and data['EMA200'].iloc[i] < data['close'].iloc[i]):

                        data['macd_signal_line_crossovers'].iloc[i] = 'Buy'
                        
                    elif (data['macd_signal_line'].iloc[i-1] < data['macd_line'].iloc[i-1] 
                                and data['macd_signal_line'].iloc[i] >= data['macd_line'].iloc[i]
                                and data['macd_signal_line'].iloc[i-1] > 0 
                                and data['macd_line'].iloc[i-1] > 0
                                and data['macd_signal_line'].iloc[i] > 0
                                and data['macd_line'].iloc[i] > 0 :
                                and data['EMA200'].iloc[i] > data['close'].iloc[i]):

                        data['macd_signal_line_crossovers'].iloc[i] = 'Sell'
            ```

            __Zero Line Crossovers__

                * Support by considering the Signal Line Crossovers in the correct side of the zero line 

        Note:
            * MACD only perform well when is in a trend so is used a EMA200 over close price 
            * This will performe less trades but increase the accuracy

        https://es.tradingview.com/support/solutions/43000502344/
        '''

        # Daily
        data['macd_close_ema12'] = pta.ema(data['close'], length=12)
        data['macd_close_ema26'] = pta.ema(data['close'], length=26)
        data['macd_close_ema200'] = pta.ema(data['close'], length=200)
        data['macd_line'] = data['macd_close_ema12'] - data['macd_close_ema26']
        data['macd_signal_line'] = pta.ema(data['macd_line'], length=9)
        data['macd_histogram'] = data['macd_line'] - data['macd_signal_line']

        current = data.iloc[-1]
        previous = data.iloc[-2]

        # Signal Line Crossovers
        if (previous['macd_signal_line'] > previous['macd_line'] 
                    and current['macd_signal_line'] <= current['macd_line'] 
                    and previous['macd_signal_line'] < 0 
                    and previous['macd_line'] < 0
                    and current['macd_signal_line'] < 0
                    and current['macd_line'] < 0 
                    and current['macd_close_ema200'] < current['close']):

            macd_signal = 'Buy'
            macd_relevance = 86
            
        elif (previous['macd_signal_line'] < previous['macd_line']
                    and current['macd_signal_line'] >= current['macd_line']
                    and previous['macd_signal_line'] > 0 
                    and previous['macd_line'] > 0
                    and current['macd_signal_line'] > 0
                    and current['macd_line'] > 0
                    and current['macd_close_ema200'] > current['close']):

            macd_signal = 'Sell'
            macd_relevance = 86
        
        else:
            macd_signal = 'Flat'
            macd_relevance = 0

        self.macd_signal = macd_signal
        self.macd_EMA26 = current['macd_close_ema26']
        self.macd_EMA12 = current['macd_close_ema12']
        self.macd_Signal_Line = current['macd_signal_line']
        self.macd_relevance = macd_relevance

        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                                    'Function': ['MACD'],
                                                                    'Signal': [self.macd_signal],
                                                                    'Relevance': [self.macd_relevance]
                                                                })], ignore_index=True) 

    ## VOLUME WIP ##
    '''
    Fundamental:
        * This functions measure the Volume.
        * Volume refers to the number of shares transacted per day. 
        * high volumes of trading can infer a lot about investors outlook on a market or security. 
        A significant price increase along with a significant volume increase, for example, 
        could be a credible sign of a continued bullish trend or a bullish reversal. Adversely, 
        a significant price decrease with a significant volume increase can point to a continued bearish trend or a bearish trend reversal. 
    '''
    
    def get_fixed_volume_profile(self, data):
        '''
        Fundamental:    
            * Fixed Range Volume Profile Indicator 
            * This volume profile tool lets you analyse how much tranding volume occured at a specific price level over specific period of times. 
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
        
        
        !! Fazer !!
        https://www.youtube.com/watch?v=5gsBD-XONRE&t=234s
        
        https://www.jumpstarttrading.com/volume-profile/

        '''

    def get_volume_pvi_nvi(self, data):
        '''
        Fundamental:
            * Positive Volume Index & Negative Volume Index
            * The PVI and NVI are both based on the previous day’s trading volume and a security’s market price. 
            When trading volume increases from the previous day the PVI is adjusted. When trading volume decreases from the previous day the NVI is adjusted.
            * If current volume is lower than the previous day's volume, PVI is unchanged.
            * PVI shows what the uninformed investors are doing, while the Negative Volume Index (NVI) shows what the smart investors are doing.
            * Fosback's research, which encompassed the period from 1941 to 1975, suggested that when the PVI is below its one-year average, there is a 67% chance of a bear market. 
            If the PVI is above its one-year average, the chance of a bear market drops to 21%.
            
        Conditions:
            
            If Volume > i-1 Volume:
                pvi change
            Else:
                pvi change = i-1 pvi 
                
            If pvi == i-1 pvi:
                pvi_trend = 'Less Volume'
            Elif pvi > i-1 pvi:
                pvi_trend = 'More Volume'    
            Elif pvi < i-1 pvi:
                pvi_trend = 'Less Volume'
                
            If Volume < i-1 Volume:
                nvi change
            Else:
                nvi change = i-1 nvi 
                
            If nvi == i-1 nvi:
                nvi_trend = 'More Volume'
            Elif nvi > i-1 nvi:
                nvi_trend = 'Less Volume'    
            Elif nvi < i-1 nvi:
                nvi_trend = 'More Volume'
                
            * NVI > MA255 then 96% 'Buy' and 4% 'Sell'
            * PVI	> MA255 then 79% 'Buy' and 21% 'Sell'
            * NVI	< MA255 then 47% 'Buy' and 53% 'Sell'
            * PVI	< MA255 then 33% 'Buy' and 67% 'Sell'

        https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/positive-volume-index
        
        https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/nvi     
        
        Norman Fosback. "Stock Market Logic," Page 123. Dearborn Financial Publishing, 1993.
        '''
        
        data['pvi'] = 0.00

        data.at[0, 'pvi'] = 1000.00

        data['nvi'] = 0.00

        data.at[0, 'nvi'] = 1000.00

        data['pvi_trend'] = None
        data['nvi_trend'] = None

        data['pvi_signal'] = None
        data['nvi_signal'] = None
        data['pvi_relevance'] = None
        data['nvi_relevance'] = None
        
        for i in range(1, len(data)):
            if data.iloc[i].volume > data.iloc[i-1].volume:
                pvi_change = ((data.iloc[i].close - data.iloc[i-1].close) / data.iloc[i-1].close) * data.iloc[i-1].pvi
                data.at[i, 'pvi'] = data.iloc[i-1].pvi + pvi_change
            else:
                data.at[i, 'pvi'] = data.iloc[i-1].pvi
                    
        for i in range(1, len(data)):
            if data.iloc[i].volume <  data.iloc[i-1].volume:
                nvi_change = ((data.iloc[i].close - data.iloc[i-1].close) / data.iloc[i-1].close) * data.iloc[i-1].nvi
                data.at[i, 'nvi'] = data.iloc[i-1].nvi + nvi_change
            else:
                data.at[i, 'nvi'] = data.iloc[i-1].nvi

        for i in range(1, len(data)):
            if data.at[i, 'pvi'] == data.at[i-1, 'pvi']:
                data.at[i, 'pvi_trend'] = 'Less Not Smart Volume'
            elif data.at[i, 'pvi'] > data.at[i-1, 'pvi']:
                data.at[i, 'pvi_trend'] = 'More Not Smart Volume'
            elif data.at[i, 'pvi'] < data.at[i-1, 'pvi']:
                data.at[i, 'pvi_trend'] = 'Less Not Smart Volume'

        for i in range(1, len(data)):
            if data.at[i, 'nvi'] == data.at[i-1, 'nvi']:
                data.at[i, 'nvi_trend'] = 'More Smart Volume'
            elif data.at[i, 'nvi'] < data.at[i-1, 'nvi']:
                data.at[i, 'nvi_trend'] = 'Less Smart Volume'
            elif data.at[i, 'nvi'] > data.at[i-1, 'nvi']:
                data.at[i, 'nvi_trend'] = 'More Smart Volume'
                
        data['pvi_EMA255'] = pta.ema(data.pvi, length=255)
        data['nvi_EMA255'] = pta.ema(data.nvi, length=255)

        pvi_now = data.iloc[-1].pvi
        nvi_now = data.iloc[-1].nvi
        
        pvi_EMA255 = data.iloc[-1].pvi_EMA255
        nvi_EMA255 = data.iloc[-1].nvi_EMA255
        
        if nvi_now > nvi_EMA255:
            nvi_signal = 'Buy'
            nvi_relevance = 80#96
        else:
            nvi_signal = 'Sell'
            nvi_relevance = 53

        if pvi_now > pvi_EMA255:
            pvi_signal = 'Buy'
            pvi_relevance = 70#79
        else:
            pvi_signal = 'Sell'
            pvi_relevance = 58#67    
            
        self.pvi_signal = pvi_signal
        self.pvi_now = pvi_now
        self.pvi_relevance = pvi_relevance

        self.nvi_signal = nvi_signal
        self.nvi_now = nvi_now
        self.nvi_relevance = nvi_relevance
        
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                                    'Function': ['PVI not Smart'],
                                                                    'Signal': [self.pvi_signal],
                                                                    'Relevance': [self.pvi_relevance]
                                                                })], ignore_index=True) 

        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                                    'Function': ['NVI Smart'],
                                                                    'Signal': [self.nvi_signal],
                                                                    'Relevance': [self.nvi_relevance]
                                                                })], ignore_index=True) 

    def combined_rsi_bollinger(self, data, sma_period ,standard_deviation_sma, RSI_Period):
        '''
        This function measures measures possible trades combining EMA 200 crossover with EMA 48 and Bollinger Bands
        
        Fundamental:
            * Bollinger Bands are envelopes plotted at a standard deviation level above and below a simple 
            moving average of the price. Because the distance of the bands is based on standard deviation,
            they adjust to volatility swings in the underlying price.
            * RSI Interval of [30-70]
            * Period = 14
            * Standard Deviation = 2
            * Threshold of Bands width = mean of the width
            
        Conditions:
            * Buy = RSI < 30 and Last Close Price <= Lower Band
            * Sell = RSI > 70 and Last Close Price >= Upper Band
            * Flat = Else  
        '''
        
        # Daily View
        data_bb = pta.bbands(data.close, length=sma_period, std=standard_deviation_sma)
        data = data.join(data_bb)
        
        # Last close_price
        last_close_price = data['close'].iloc[-1]
        bbl_last = data['BBL_14_2.0'].iloc[-1]
        bbu_last = data['BBU_14_2.0'].iloc[-1]
        bbb_last = data['BBB_14_2.0'].iloc[-1]
        bbb_mean = data['BBB_14_2.0'].mean()

        # Rsi
        rsi = pta.rsi(data.close, length=RSI_Period)
        data = data.join(rsi)
        rsi_now = rsi.iloc[-1] 

        # Finding signal
        if bbb_last > bbb_mean:
            if last_close_price < bbl_last and rsi_now < 30: 
                self.comb_bb_rsi_signal = 'Buy'
                self.comb_bb_rsi_relevance = 95
            elif last_close_price > bbu_last and rsi_now > 70:
                self.comb_bb_rsi_signal = 'Sell'
                self.comb_bb_rsi_relevance = 95
            else:
                self.comb_bb_rsi_signal = 'Flat'
                self.comb_bb_rsi_relevance = 0
        else:
            self.comb_bb_rsi_signal = 'Flat'
            self.comb_bb_rsi_relevance = 0

        # Stoploss Definitions
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                                    'Function': ['Combined RSI & Bollinger'],
                                                                    'Signal': [self.comb_bb_rsi_signal],
                                                                    'Relevance': [self.comb_bb_rsi_relevance]
                                                                })], ignore_index=True) 

   
'''
## 5 titans ##

# Charles H. Dow

The Dow Theory is an approach to trading developed by Charles H. Dow, who, with Edward Jones and Charles Bergstresser, 
founded Dow Jones & Company, Inc. and developed the Dow Jones Industrial Average in 1896. 

https://www.investopedia.com/terms/d/dowtheory.asp
https://www.wsj.com/public/resources/documents/info-DJTimeline0706.html


## Correlações a adicionar ##

https://qontigo.com/the-top-10-cross-asset-correlations-to-watch/

'''

