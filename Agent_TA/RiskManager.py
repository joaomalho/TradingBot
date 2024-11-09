'''
This process will manage the risk of each trade, lote size, risk/reward racio (which will be crucial in decision)
'''
import pandas as pd


class Risk_Manager():

    def __init__(self) -> None:
        # Stop Loss and Take profit
        self.stoploss = None
        self.decision_df = pd.DataFrame(columns=['Function', 'Signal'])

    def risk_manager(self, cp_results):
        '''
        This function manage the risk security for each trade
        '''
        # Candles Stoploss and Takeprofit risk management
        cp_results_new = cp_results[cp_results["Function"]!= "Base"]
        stoploss_values = cp_results_new.loc[cp_results_new['Signal'] != 'Flat', 'Stoploss']
        if not stoploss_values.empty:
            self.stoploss = stoploss_values.iloc[0]
        else:
            self.stoploss = "tail"
            
        return self.stoploss


    def get_decision(self, trend_metrics_df, candle_patterns_df):
        '''
        Function to get and "decision" over signals results 
        
        Fundamentals:
            * Decision consistes in sum all the metrics results by each signal and calculate the relevance of each one.           
        '''

        cp_results = candle_patterns_df[candle_patterns_df["Function"]!= "Base"]

        # Filtrar os sinais que não são 'Flat'
        candle_signal = cp_results[cp_results['Signal'] != 'Flat']['Signal']
        candle_pattern = cp_results[cp_results['Signal'] != 'Flat']['Function']

        trend_signal = trend_metrics_df[trend_metrics_df['Signal'] != 'Flat']['Signal']
        num_trend_signal = len(trend_signal)

        if not candle_signal.empty:
            
            if candle_pattern.iloc[0] != "Engulfing":
                decision_signal = candle_signal.iloc[0]

        elif trend_signal.empty:
            decision_signal = "Flat"
        elif num_trend_signal == 1:
            if not candle_signal.empty and candle_pattern.iloc[0] == "Engulfing" and trend_signal.iloc[0] == candle_signal.iloc[0]:
                decision_signal = trend_signal.iloc[0]
            else:

                decision_signal = trend_signal.iloc[0] # Teste
                # decision_signal = 'Flat' # Original

        elif num_trend_signal == 2:
            unique_signals = trend_signal.unique()
            if len(unique_signals) == 1:
                decision_signal = unique_signals[0]
            else:
                decision_signal = 'Flat'
        elif num_trend_signal == 3:
            signal_counts = trend_signal.value_counts()
            if len(signal_counts) == 1:
                decision_signal = signal_counts.idxmax()
            elif len(signal_counts) == 2:
                decision_signal = signal_counts.idxmax()
            else:
                decision_signal = 'Flat'
        else:
            decision_signal = 'Flat'

        return decision_signal
        
