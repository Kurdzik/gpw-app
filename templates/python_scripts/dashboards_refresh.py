import sqlalchemy
import pandas as pd
import shutil
import os

conn_string = os.environ['DB_CONN_STRING']

engine = sqlalchemy.create_engine(conn_string)
conn = engine.connect()

def get_fin_data_from_db(ticker,time):

    if ticker!='ALL':

        q = f"""select distinct Ticker from gpw.notowania"""
        df = pd.read_sql(q,con=conn)

