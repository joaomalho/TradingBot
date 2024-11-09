'''
This file measures the tailing stoploss
'''
import pandas as pd
import MetaTrader5 as mt5


class Tailing_Stoploss():
    
    def __init__(self) -> None:
        
        self.new_stop_loss = None
    
    def modify_position_tailling(self, tailling_value): # new_take_profit):
        '''
        This function update the stoploss in the open trade.
        
        Fundamentals:
            * Tailling StopLoss consistes in constantly update the stoploss to a small value below the current price in order
            to collect the maximo profit as possible and preventing big losses due volatily big moves
            
        Conditions:
            * Only occur when is 1 position opened
            * new_stop_loss = price_current - TAILLING_VALUE
        '''                    
        
        positions = mt5.positions_get()
        positions_df = pd.DataFrame([[i.symbol] for i in positions],
                        columns=['symbol'])
        
        tickers_to_process = positions_df['symbol'].tolist()
            
        for ticker in tickers_to_process:
            
            # Get data from trades
            order_number = mt5.positions_get(symbol=ticker)[0][0]
            symbol = ticker
            price_current = mt5.positions_get(symbol=ticker)[0][13]
            profit = mt5.positions_get(symbol=ticker)[0][15]
            type = mt5.positions_get(symbol=ticker)[0][5] # 0 = Buy | 1 = Sell
            stoploss = mt5.positions_get(symbol=ticker)[0].sl
            
            # == Control of execution == # 
            # Buy & profit positive
            if type == 0 and profit > 0: 
                self.new_stop_loss = price_current - tailling_value 
                if self.new_stop_loss > stoploss: # ver se o current price tem o mesmo time frame de atualização
                    # Create the request
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": symbol,
                        "sl": self.new_stop_loss,
                        #"tp": new_take_profit,
                        "position": order_number
                    }
                    # Send order to MT5
                    order_result = mt5.order_send(request)
                        
                else:
                    order_result = 'Tailling Stop Loss not updated'
                
            # Sell & profit positive 
            elif type == 1 and profit > 0: 
                self.new_stop_loss = price_current + tailling_value 
                if self.new_stop_loss < stoploss:    
                    # Create the request
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": symbol,
                        "sl": self.new_stop_loss,
                        #"tp": new_take_profit,
                        "position": order_number
                    }
                    # Send order to MT5
                    order_result = mt5.order_send(request)
                else:
                    order_result = 'Tailling Stop Loss not updated'
                    
            else:
                order_result = 'Tailling Stop Loss not updated'
            
            return order_result