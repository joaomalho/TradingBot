'''
This file compile all the metrics result and relevance o perform the overall result of the trend and pass to execution file
'''
import pandas as pd
import datetime as dt
from connections import Connections

class Decision():

    def __init__(self) -> None:

        self.decision_df = pd.DataFrame(columns=['Function', 'Signal', 'Relevance'])
                

    def get_decision(self, trend_metrics_df, candle_patterns_df):
        '''
        Function to get and "decision" over signals results 
        
        Fundamentals:
            * Decision consistes in sum all the metrics results by each signal and calculate the relevance of each one.
            
        Conditions:
            * Total Relevance of Buy >= Min Buy Relevance THEN buy
            * Total Relevance <= Min Sell Relevance THEN sell
            * Else = Flat
            
        '''
        
        self.combined_df = pd.DataFrame()
        
        # Concatenate the DataFrames vertically
        self.combined_df = pd.concat([self.combined_df,
                                        trend_metrics_df, 
                                        candle_patterns_df, 
                                        ],ignore_index=True)
        
         
        # Daily View
        day_buy_combined_df = self.combined_df[(self.combined_df['Signal'] == 'Buy')]
        day_sell_combined_df = self.combined_df[(self.combined_df['Signal'] == 'Sell')]

        # if self.SYMBOL == 'EURUSD':
        #     decision_signal = self.combined_df[(self.combined_df['Function'] == 'Combined RSI & Bollinger') & (self.combined_df['View'] == 'Hourly')]['Signal']
        #     # decision_signal = self.combined_df[(self.combined_df['Function'] == 'EMAs_Crossover') & (self.combined_df['View'] == 'Hourly')]['Signal']
            
        # else:
        #     ## V1 - By Weight Average ##
        
            # if len(hour_buy_combined_df) != 0:
            #     hour_buy_avg_relevance = hour_buy_combined_df['Relevance'].sum() / len(hour_buy_combined_df)
            # else:
            #     hour_buy_avg_relevance = 0
                
            # if len(hour_sell_combined_df) != 0:
            #     hour_sell_avg_relevance = hour_sell_combined_df['Relevance'].sum() / len(hour_sell_combined_df)
            # else:
            #     hour_sell_avg_relevance = 0
                
            # if len(day_buy_combined_df) != 0:
            #     daily_buy_avg_relevance = day_buy_combined_df['Relevance'].sum() / len(day_buy_combined_df)
            # else:
            #     daily_buy_avg_relevance = 0
                
            # if len(day_sell_combined_df) != 0:
            #     daily_sell_avg_relevance = day_sell_combined_df['Relevance'].sum() / len(day_sell_combined_df)
            # else:
            #     daily_sell_avg_relevance = 0


        ## V2 - By Number of Indicators ##
       
        daily_buy_avg_relevance = len(day_buy_combined_df[day_buy_combined_df['Relevance'] != 0])
            
        daily_sell_avg_relevance = len(day_sell_combined_df[day_sell_combined_df['Relevance'] != 0])

        self.decision_df = pd.concat([self.decision_df, pd.DataFrame({
                                                        'Function': ['Decision'],
                                                        'Signal': ['Buy'],
                                                        'Relevance': [daily_buy_avg_relevance]
                                                    })], ignore_index=True)

        self.decision_df = pd.concat([self.decision_df, pd.DataFrame({
                                                        'Function': ['Decision'],
                                                        'Signal': ['Sell'],
                                                        'Relevance': [daily_sell_avg_relevance]
                                                    })], ignore_index=True)
        self.decision_df['Time'] = dt.datetime.now()
        self.decision_df['Relevance'] = pd.to_numeric(self.decision_df['Relevance'], errors='coerce')


        # Filter the DataFrame to include only rows where the accuracy is above 3
        ## V1 ## filtered_df = self.decision_df[self.decision_df['Accuracy'] > 50.00]
        
        filtered_df = self.decision_df[self.decision_df['Relevance'] >= 2]
        
        # Check if there are any rows that meet the condition
        if not filtered_df.empty:
            # Find the index of the row with the maximum value in the "Accuracy" column
            max_accuracy_index = filtered_df['Relevance'].idxmax()

            # Get the row with the maximum value in the "Accuracy" column
            max_accuracy_row = self.decision_df.loc[max_accuracy_index]

            decision_signal = max_accuracy_row['Signal']
            
        else:
            # Handle the case when no rows meet the criteria
            decision_signal = 'Flat'
        
        # Store Results of Decisions
        # Infinite store!!!!
        # Connections().sql_connect(table_db_name = 'decisions', table=self.decision_df, ifexists='append')

        return decision_signal