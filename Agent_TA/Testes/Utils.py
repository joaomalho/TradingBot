'''
    This file is responsible to organize and detail all the Variables across the grid 
'''

# Python Libraries
import os
import pandas as pd
from dotenv import load_dotenv
from binance.client import Client

class Utils():
    def __init__(self, ticker) -> None:
        
        # ============= VARIAVEIS FIXAS ============= #'        
        # self.MAGIC = 100 # Ref
        # self.VOLUME = 0.02 # Size of lot
        # self.START_POSITION = 0 
        # self.NUMBER_BARS = 1000
        # self.NUMBER_BARS_vp = 99999

        # ====== Utilidades ====== #  
            # Tempo atual
        # self.current_time = dt.datetime.now().time()
        #     # Exposição atual
        # self.exposure = self.get_exposure(self.SYMBOL)
        #     # Ticker do Par
        # self.tick = mt5.symbol_info_tick(self.SYMBOL)
        #     # Preço da posição atual
        # self.position_current_price = self.tick[1]

        self.data_1h = pd.DataFrame(mt5.copy_rates_from_pos(ticker, mt5.TIMEFRAME_H1, self.START_POSITION, self.NUMBER_BARS_vp))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
        # self.data_1h.rename(columns={'tick_volume': 'volume'}, inplace=True)
        
        

        # ============= COLETA DE DADOS ============= #
        if market_type == 'Cambial':
            if timeframe == "15M":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_M15, self.START_POSITION, self.NUMBER_BARS))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
            
            if timeframe == "30M":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_M30, self.START_POSITION, self.NUMBER_BARS))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
                
            if timeframe == "1H":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_H1, self.START_POSITION, self.NUMBER_BARS))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
                
            if timeframe == "4H":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_H4, self.START_POSITION, self.NUMBER_BARS))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
 
            if timeframe == "1D":
                # Use Metatrader
                self.data = pd.DataFrame(mt5.copy_rates_from_pos(self.SYMBOL, mt5.TIMEFRAME_D1, self.START_POSITION, self.NUMBER_BARS))[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
            

            self.data.rename(columns={'tick_volume': 'volume'}, inplace=True)


    # ======= INFORMATION PART ======= #
    def get_exposure(self, symbol):
        '''
        Deteção de exposição atual
        '''
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            pos_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())
            exposure = pos_df['volume'].sum()
        else:
            exposure = self.VOLUME
        return exposure    
    
    def login():
        '''
        Esta função tem como utilidade fazer login na plataforma metatrater
        '''
        # Carrega o arquivo .env
        load_dotenv()

        # Acessa as variáveis
        api_key = os.getenv("API_KEY")
        api_secret = os.getenv("API_SECRET")

        client = Client(api_key,api_secret)

    def get_tickerlist(self):
        tickerlists = pd.DataFrame([[symbol.name, symbol.path, symbol.description] for symbol in mt5.symbols_get()], columns = ['Ticker', 'Path', 'Description'])

        tickerlists['type'] = np.where(tickerlists['Path'].str.contains("forex", case=False), 'cambial',
                                    np.where(tickerlists['Path'].str.contains("crypto", case=False), 'crypto',
                                                np.where(tickerlists['Path'].str.contains("indices", case=False), 'indice',
                                                        np.where(tickerlists['Path'].str.contains("commodities", case=False), 'commodity',
                                                                np.where(tickerlists['Path'].str.contains("stock", case=False), 'stock', None)
                                                                )
                                                        )
                                            )
                                    )
        self.tickerlists = tickerlists


