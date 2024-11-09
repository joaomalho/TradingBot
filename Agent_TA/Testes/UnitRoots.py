'''
This class tests the existence of unit roots and consequently determines if time series is stationary or not 
'''
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller

class UnitRoots():
    def __init__(self) -> None:
        self.random_walk = 1

    def get_dickeyfuller(self, data : pd.DataFrame):
        '''
        This function apply a Dickey Fuller Test over the closing price of the data detecting if this regard a stationary behaviour.

        Fundamental:
            * This funtion measures stationarity, stationarity is a type of data that regard statistical properties that not change over time, 
            meaning constant mean, variance and autocorrelation, and this properties are independent of time.
            * In order to detect the evidence of stationarity time series is differenced until second-order differencing. 
            * ADF test the presence of a unit root, is a unit root is present then is not stationary
        
        Conditions:
            * If adf p-value > 0.05:
                difference(close)
                If second_adf p-value < 0.05:
                    dif

        '''

        ADF_result = adfuller(data['close'])
                
        if ADF_result[1] > 0.05:
            first_diff = np.diff(data['close'], n=1)
            ADF_result_1 = adfuller(first_diff)
            
            if ADF_result_1[1] > 0.05:
                second_diff = np.diff(first_diff, n=1)
                ADF_result_2 = adfuller(second_diff)
        
                if ADF_result_2[1] < 0.05:
                    self.random_walk = 1
        
        else:
            self.random_walk = 0
