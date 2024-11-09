import MetaTrader5 as mt5
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine


class Connections():
    def __init__(self) -> None:
        self.mycursor = None
        self.engine = None

    def metatrader_connect(self):
        ## == Metrader connection == ##
        mt5.initialize()
        mt5.login(51116412, '39sz2vL3', 'ICMarketsSC-Demo')

    def sql_connect(self, table_db_name, table, ifexists):
        self.db = mysql.connector.connect(
            host='localhost',
            user='matris_user',
            password='Matrisv3t16',
            database='MATRIS'
        )
        self.mycursor = self.db.cursor()
        self.engine = create_engine('mysql+pymysql://matris_user:Matrisv3t16@localhost/MATRIS')
        
        
        with self.engine.connect() as connection:

            self.tosql = table.to_sql(table_db_name, self.engine, if_exists=ifexists, index=False)

        self.mycursor.close()
        self.db.close()

