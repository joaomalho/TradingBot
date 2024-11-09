'''
This Main represents the interface of the engine.
'''

from run import engine
import customtkinter as ctk

class FrontEnd(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ============= Variables ============= #
        self.market_type = None
        self.timeframe = None
        self.ticker = None
        self.autotrade_set = None
        self.start = None
        self.stop = False

        # ============= Aplication Window ============= #
        self.geometry("600x500")
        self.title("Matris Trading Engine ")

        # ============= Widgets ============= #

        # == Select Type of Market == # 
        self.label_type = ctk.CTkLabel(self, text="Select Type of Market", fg_color="transparent")
        self.label_type.grid(row=0, column=0)

        self.combobox_type_var = ctk.StringVar(value="")
        self.combobox_type = ctk.CTkComboBox(self, values=["", "Stock", "Cambial"],
                                                command=self.combobox_type_callback, 
                                                variable=self.combobox_type_var)
        
        self.combobox_type.grid(row=0, column=1, padx=20, pady=10)

        # == Select Timeframe == # 
        self.label_timeframe = ctk.CTkLabel(self, text="Select Timeframe", fg_color="transparent")
        self.label_timeframe.grid(row=1, column=0)

        self.combobox_timeframe_var = ctk.StringVar(value="")
        self.combobox_timeframe = ctk.CTkComboBox(self, values=["", "15M", "30M", "1H", "4H", "1D"],
                                                command=self.combobox_timeframe_callback, 
                                                variable=self.combobox_timeframe_var)
        self.combobox_timeframe.grid(row=1, column=1, padx=20, pady=10)

        # == Select AutoTrade == # 
        self.label_autotrade = ctk.CTkLabel(self, text="Autotrade ?", fg_color="transparent")
        self.label_autotrade.grid(row=2, column=0)

        self.switch_autotrade_var = ctk.StringVar(value="on")
        self.switch_autotrade = ctk.CTkSwitch(self, command=self.switch_autotrade_event,
                                 variable=self.switch_autotrade_var, onvalue="on", offvalue="off")
        
        self.switch_autotrade.grid(row=2, column=1, padx=20, pady=10)

        # == Select ticker == #
        self.label_ticker = ctk.CTkLabel(self, text="Select ticker:", fg_color="transparent")
        self.label_ticker.grid(row=3, column=0)

        self.combobox_ticker_var = ctk.StringVar(value="")
        self.combobox_ticker = ctk.CTkComboBox(self, values=["Top10","EURUSD","Crypto"],
                                                command=self.combobox_ticker_callback, 
                                                variable=self.combobox_ticker_var)

        self.combobox_ticker.grid(row=3, column=1, padx=20, pady=10)

        # == Start Bot == #
        self.button_start = ctk.CTkButton(self, text="Start", command=self.button_start_click)
        self.button_start.grid(row=4, column=0, padx=20, pady=20)
       
        # == Stop Bot == #
        self.button_start = ctk.CTkButton(self, text="Stop", command=self.button_stop_click)
        self.button_start.grid(row=4, column=1, padx=20, pady=20)

        # == Exit Bot == #
        self.button_exit = ctk.CTkButton(self, text="Exit Matriz", command=self.button_exit_click)
        self.button_exit.grid(row=4, column=2, padx=20, pady=20)
        
    # ============= Callbacks ============= #
    
    def combobox_type_callback(self, choice):
        print("combobox dropdown clicked:", choice)
        self.market_type = choice

    def combobox_timeframe_callback(self, choice):
        print("combobox dropdown clicked:", choice)
        self.timeframe = choice

    def combobox_ticker_callback(self, choice):
        print("combobox dropdown clicked:", choice)
        self.ticker = choice

    def switch_autotrade_event(self):
        print("switch toggled, current value:", self.switch_autotrade_var.get())
        self.autotrade_set = self.switch_autotrade_var.get()

    def button_start_click(self):
        self.start = True
        engine().execute_strategy(self.market_type, self.timeframe, self.ticker, self.autotrade_set, self.stop)

    def button_stop_click(self):
        self.stop = True
        
    def button_exit_click(self):
        self.destroy()
        
app = FrontEnd()
app.mainloop()
