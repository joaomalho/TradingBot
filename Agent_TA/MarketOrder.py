'''
This file is responsible for market order execution
'''
import pandas as pd
import MetaTrader5 as mt5
from connections import Connections


class Market_Order_Execution():
    def __init__(self) -> None:
        
        self.order_result = None
    
    def market_order(self, tick, symbol, volume, magic, stoploss, current_price, bagging_signal):
        '''
        This function will send the request to platform and request to open the position
        '''
        
        order_dict = {'Buy': 0, 'Sell': 1}
        price_dict = {'Buy': tick.ask, 'Sell': tick.bid}
        
        # take_profit = {'buy': upper_band - stoploss, 'sell': lower_band + stoploss}
        stop_loss = {'Buy': current_price - stoploss, 'Sell': current_price + stoploss} 
        
        request = {
            'action': mt5.TRADE_ACTION_DEAL, # action is to DEAL
            'symbol': symbol,
            'volume': volume, 
            'type': order_dict[bagging_signal], # Buy or Sell
            'price': price_dict[bagging_signal], # Buy at Curent ask price
            #'deviation': deviation, #INT # Within deviation range when market open THEN make the DEAL
            'magic': magic, #INT # Each order have a unique magic number to identify 
            #'tp': take_profit[order_type], # Take Profit
            'sl': stop_loss[bagging_signal], # Stop Loss default
            'comment': 'python order',
            'type_time': mt5.ORDER_TIME_GTC, # Good till Cancel order
            'type_filling': mt5.ORDER_FILLING_IOC, # Imidiate or Cancel order (Used in IC markets)
        }

        order_result = mt5.order_send(request)
        
        print(order_result)
                    
        # Store Results of Orders
        Connections().sql_connect(table_db_name = 'market_orders', table=pd.DataFrame([order_result]), ifexists='append')

        self.order_result = order_result 
            