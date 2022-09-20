import sqlalchemy
import pandas as pd
import os
from .gpw_functions import map_financial_data
import time
import numpy as np



conn_string = os.environ['DB_CONN_STRING']

engine = sqlalchemy.create_engine(conn_string)
conn = engine.connect()

# get all data
q = f"""select * from gpw.notowania"""
df = pd.read_sql(q,con=conn)

# get all tickers
q = f"""select distinct Ticker from gpw.notowania"""
tickers = pd.read_sql(q,con=conn)

# upload the data on separate schemas if the data is avaiable
for ticker in tickers:
    
    time.sleep(np.random.randint(5,20))

    df, BS, RZiS, CF = map_financial_data(df.loc[df['Ticker']==ticker],db_conn=conn)
    
    if df!='not avaiable':
        df.to_sql(ticker,schema='predictors',if_exists='replace',con=conn)
    else:
        continue

    if BS!='not avaiable':
        BS.to_sql(ticker,schema='BS',if_exists='replace',con=conn)
    else:
        continue
    
    if RZiS!='not avaiable':
        RZiS.to_sql(ticker,schema='RZiS',if_exists='replace',con=conn)
    else:
        continue

    if CF!='not avaiable':
        CF.to_sql(ticker,schema='CF',if_exists='replace',con=conn)
    else:
        continue