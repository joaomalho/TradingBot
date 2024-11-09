'''
This process will manage the risk of each trade, lote size, risk/reward racio (which will be crucial in decision)
'''
import MetaTrader5 as mt5

class Risk_Manager():

    def __init__(self) -> None:
        # Stop Loss and Take profit
        self.DEFAULT_STOP_LOSS = 0.01# (self.spread*0.0005) # Update of stop loss | Half pip in order to control big volatility  
        self.TAILLING_VALUE = 0.001  # Update of stop loss | Half pip in order to control big volatility

    def market_order_size(self, winrate, current_price):
        '''
        This function manage the market order size per each trade
        
        Fundamental:
        * Following the 1% rule, this rule of thumb suggest that should never invest more then 1% of trading account in a single trade.  
        * This will adjust according the confidence of the trade which FOR NOW IS WEIGHTED BY WIN RATE % (?????)
        * TEMPORY : Lot Size is weighted by win rate over 1 lot, max trade is 1 lot when 100% Win rate AVG

        Lot Value = Lot Size * Current Price
        Lot Size = Lot Value / Current Price 
        '''

        self.account_balance = mt5.account_info().balance

        self.lote_value = self.account_balance*.01
        # self.Lote_Size = round(1 * (winrate/100), 2) 
        self.Lote_Size = 0.02
        self.Lote_Size_Max = (self.lote_value / current_price) * (winrate/100) # To Develop after stop loss and tak profits

        return self.Lote_Size

        
