'''
This file regards the detection of candles paterns.

Fundamental:
    * For patterns that regard 1 candle the model look to the last candle
    * For patterns that regard more than 1 candle the model look to the last candles, 4, 5, 6...

Note:
    * Each candle pattern detected is included in the corresponding columns with a 1, otherwise 0
    to get the last candle pattern just need to be regarded the 1.

Implementation:
    * Tri-Star Bullish engolfing

'''

import pandas as pd

class Candles_Patterns():
    
    '''
    This class regard a function per each candle pattern
    This function measures which is the actual candles pattern and result in a bullish or bearish trend 
        
    Fundamental:
        * Measure the candle pattern for timeframes of 1 Day and 1 Hour, meaning that each candle represents
        1 Day and 1 Hour respectively 
        
    '''

    def __init__(self) -> None:
        
        self.result_df = pd.DataFrame(columns=['Function', 'Signal', 'Relevance'])
        self.data_candles = pd.DataFrame()
        
        # Pattern and Signal detection
        self.candle_pattern = None 
        self.candle_signal = None 
        self.candle_relevance = None 
        self.candle_type = None


    def candle_basic_signal(self, data : pd.DataFrame):
        '''
        This function perform a for loop measure the candles types, bearish ou bullish and shadows size comparatively with body size.
        
        Conditions:
            * bullish = Close Price > Open Price
            * bearish = Close Price < Open Price
            * flat = Else
        '''
        # Data
        last_candle = data.tail(1)
        
        if last_candle.close.item() > last_candle.close.item():
            candle_pattern = 'Base Bullish'
            candle_signal = 1
            candle_relevance = 0
                        
        elif last_candle.close.item() < last_candle.open.item():
            candle_pattern = 'Base Bearish'
            candle_signal = -1
            candle_relevance = 0
            
        else:
            candle_pattern = 'Base Flat'
            candle_signal = 0
            candle_relevance = 0

        self.candle_pattern = candle_pattern 
        self.candle_signal = candle_signal
        self.candle_relevance = candle_relevance
   
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                    'Function': [self.candle_pattern],
                                                    'Signal': [self.candle_signal],
                                                    'Relevance': [self.candle_relevance]
                                                })], ignore_index=True) 
            
            
    def engulfing(self, data : pd.DataFrame):
        '''
        This function detect if the last candle is a bearish or bulish engolfing
        
        Fundamental:
            * In a Bullish Engulfing pattern, the body of the second (bullish) candle should completely engulf the 
            body of the first (bearish) candle. This means that the opening price of the second candle is lower than
            the closing price of the first candle, and the closing price of the second candle is higher than the opening
            price of the first candle.
            * In a Bearish Engulfing pattern, the body of the second (bearish) candle should completely engulf the 
            body of the first (bullish) candle. This means that the opening price of the second candle is higher than
            the closing price of the first candle, and the closing price of the second candle is lower than the opening
            price of the first candle.
            * Bulish engulfing has a reversal rate of 63%. That means price closes above the top of the candlestick pattern 63% of the time.
            * Bearish performing that way 79% of the time.
        '''

        # Data
        last_candle = data.tail(1)
        second_last_candle = data.tail(2).head(1)
        third_last_candle = data.tail(3).head(1)
  
        # View
        if (second_last_candle.open.item() < second_last_candle.close.item() and third_last_candle.open.item() < third_last_candle.close.item() 
            and second_last_candle.open.item() < third_last_candle.close.item()
            and second_last_candle.close.item() > third_last_candle.open.item()
            and (last_candle.low.item() > second_last_candle.low.item()) & (last_candle.low.item() > third_last_candle.low.item())
            ):
            candle_pattern = 'Bullish Engulfing'
            candle_signal = 1
            candle_relevance = 63

        elif (second_last_candle.open.item() > second_last_candle.close.item() and third_last_candle.open.item() > third_last_candle.close.item() 
            and second_last_candle.open.item() > third_last_candle.close.item()
            and second_last_candle.close.item() < third_last_candle.open.item()
            and (last_candle.high.item() < second_last_candle.high.item()) & (last_candle.high.item() < third_last_candle.high.item())
            ):
            candle_pattern = 'Bearish Engulfing'
            candle_signal = -1
            candle_relevance = 79
        else:
            candle_pattern = 'Engulfing'
            candle_signal = 0
            candle_relevance = 0

        self.candle_pattern = candle_pattern 
        self.candle_signal = candle_signal
        self.candle_relevance = candle_relevance
   
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                    'Function': [self.candle_pattern],
                                                    'Signal': [self.candle_signal],
                                                    'Relevance': [self.candle_relevance]
                                                })], ignore_index=True) 

    def morning_star(self, data : pd.DataFrame):
        '''
        A morning star is a three-candle pattern with the low point on the second candle. 
        However, the low point is only apparent after the close of the third candle.
        High volume on the third day is often seen as a confirmation of the pattern 
        (and a subsequent uptrend) regardless of other indicators.
        
        Fundamental:
            * First candle: The first candlestick is a tall bearish candle, in line with the ongoing downward price swing. It shows that the downswing is still intact.
            * Second candle: The second candlestick is a small-bodied candle, typically a doji or a spinning top. It gaps down from the first candlestick. It can be of 
            any color, but the most important thing is that it is small and gaps below the first, in anticipation of the continuation of the existing downswing. 
            Its typical small size suggests indecision in the market. If it is a doji, the pattern is called Morning Doji Star.
            * Third candle: The third candle is bullish and quite sizeable. It opens below the second candle and closes above the midpoint of the first candle. 
            * Bullish reversal 78% of the time.
            * Bearish reversal of the upward price trend, and testing reveals that it does 71% of the time.
        '''

        # Data
        last_candle = data.tail(1)
        second_last_candle = data.tail(2).head(1)
        third_last_candle = data.tail(3).head(1)

        if(
                third_last_candle.open.item() > third_last_candle.close.item()
                and (second_last_candle.open.item() < third_last_candle.close.item()) & (second_last_candle.close.item() < third_last_candle.close.item())   
                and last_candle.open.item() < last_candle.close.item()
                and second_last_candle.open.item() < last_candle.open.item()) & (second_last_candle.close.item() < last_candle.open.item()
            ):
            candle_pattern = 'Morning Star'
            candle_signal = 1
            candle_relevance = 78
        else:
            candle_pattern = 'Morning Star'
            candle_signal = 0
            candle_relevance = 0

        self.candle_pattern = candle_pattern 
        self.candle_signal = candle_signal
        self.candle_relevance = candle_relevance

        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                    'Function': [self.candle_pattern],
                                                    'Signal': [self.candle_signal],
                                                    'Relevance': [self.candle_relevance]
                                                })], ignore_index=True) 
        
    def evening_star(self, data : pd.DataFrame):
        '''
        '''

        # Data 
        last_candle = data.tail(1)
        second_last_candle = data.tail(2).head(1)
        third_last_candle = data.tail(3).head(1)

        if(
                third_last_candle.open.item() < third_last_candle.close.item()
                and (second_last_candle.open.item() > third_last_candle.close.item()) & (second_last_candle.close.item() > third_last_candle.close.item())   
                and last_candle.open.item() > last_candle.close.item()
                and second_last_candle.open.item() > last_candle.open.item()) & (second_last_candle.close.item() > last_candle.open.item()
            ):
            candle_pattern = 'Evening Star'
            candle_signal = -1
            candle_relevance = 78
        else:
            candle_pattern = 'Evening Star'
            candle_signal = 0
            candle_relevance = 0

        self.candle_pattern = candle_pattern 
        self.candle_signal = candle_signal
        self.candle_relevance = candle_relevance

        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                    'Function': [self.candle_pattern],
                                                    'Signal': [self.candle_signal],
                                                    'Relevance': [self.candle_relevance]
                                                })], ignore_index=True) 

    def hammer(self, data : pd.DataFrame):
        '''
        '''

        # Data
        last_candle = data.tail(1)
        second_last_candle = data.tail(2).head(1)
        third_last_candle = data.tail(3).head(1)
        fourth_last_candle = data.tail(4).head(1)
        fiveth_last_candle = data.tail(5).head(1)
        
        if(
            last_candle.open.item() < last_candle.close.item()
            and ((last_candle.open.item() - last_candle.low.item())/(last_candle.close.item() - last_candle.open.item()) > 2)
            and last_candle.low.item() < second_last_candle.low.item()
            and last_candle.low.item() < third_last_candle.low.item()
            and last_candle.low.item() < fourth_last_candle.low.item()
            and last_candle.low.item() < fiveth_last_candle.low.item()
            and (((last_candle.close.item() - last_candle.open.item())/(last_candle.high.item() - last_candle.close.item())) > 3)  
        ):
                candle_pattern = 'Hammer'
                candle_signal = 1
                candle_relevance = 60
        else:
            candle_pattern = 'Hammer'
            candle_signal = 0
            candle_relevance = 0
                           
        self.candle_pattern = candle_pattern 
        self.candle_signal = candle_signal
        self.candle_relevance = candle_relevance
        
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                    'Function': [self.candle_pattern],
                                                    'Signal': [self.candle_signal],
                                                    'Relevance': [self.candle_relevance]
                                                })], ignore_index=True) 

    def hanging_man(self, data : pd.DataFrame):
        '''
        '''

        # Data
        last_candle = data.tail(1)
        second_last_candle = data.tail(2).head(1)
        third_last_candle = data.tail(3).head(1)
        fourth_last_candle = data.tail(4).head(1)
        fiveth_last_candle = data.tail(5).head(1)
        sixth_last_candle = data.tail(6).head(1)
        
        if(
            second_last_candle.open.item() < second_last_candle.close.item() 
            and ((second_last_candle.open.item() - second_last_candle.low.item())/(second_last_candle.close.item() - second_last_candle.open.item()) > 2)
            and second_last_candle.high.item() > third_last_candle.high.item()
            and second_last_candle.high.item() > fourth_last_candle.high.item()
            and second_last_candle.high.item() > fiveth_last_candle.high.item()
            and second_last_candle.high.item() > sixth_last_candle.high.item()
            and (((second_last_candle.close.item() - second_last_candle.open.item())/(second_last_candle.high.item() - second_last_candle.close.item())) > 3)  
            and last_candle.open.item() > last_candle.close.item()
        ):
                candle_pattern = 'Hanging Man'
                candle_signal = -1
                candle_relevance = 60
        else:
            candle_pattern = 'Hanging Man'
            candle_signal = 0
            candle_relevance = 0
                           
        self.candle_pattern = candle_pattern 
        self.candle_signal = candle_signal
        self.candle_relevance = candle_relevance
        
        self.result_df = pd.concat([self.result_df, pd.DataFrame({
                                                    'Function': [self.candle_pattern],
                                                    'Signal': [self.candle_signal],
                                                    'Relevance': [self.candle_relevance]
                                                })], ignore_index=True) 
 