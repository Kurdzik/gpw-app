import sqlalchemy
import pandas as pd
import os
from gpw_functions import map_financial_data
import time
import numpy as np
import time


conn_string = os.environ['DB_CONN_STRING']

engine = sqlalchemy.create_engine(conn_string)
conn = engine.connect()

# get all data
q = f"""select distinct * from gpw.notowania """
df_all = pd.read_sql(q,con=conn)

# get all tickers
q = f"""SELECT distinct "Ticker" FROM gpw.notowania order by "Ticker";"""
tickers = pd.read_sql(q,con=conn)

# upload the data on separate schemas if the data is avaiable


# I batch 
for i,ticker in enumerate(tickers.values[:200]):
    time.sleep(np.random.randint(5,7))
        
    # because we are working with the list of lists
    ticker = ticker[0]

    # check if ticker exists        
    input_df = df_all.loc[df_all['Ticker']==ticker].copy()
    print(f'len: {len(input_df)}, ticker: {ticker}, progress: {i+1}/{len(tickers.values)}')

    if len(input_df)<50:
        print(f'{ticker} not enough data')
        continue
    
    df, BS, RZiS, CF = map_financial_data(df = df_all.loc[df_all['Ticker']==ticker], db_conn = conn)
        
    if type(df)!=str:
        df.to_sql(str(ticker),schema='gpw_predictors',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} df')
        
    if type(BS)!=str:
        BS.to_sql(str(ticker),schema='gpw_BS',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} BS')
        
    if type(RZiS)!=str:
        RZiS.to_sql(str(ticker),schema='gpw_RZiS',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} RZiS')
        
    if type(CF)!=str:
        CF.to_sql(str(ticker),schema='gpw_CF',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} CF')
        continue


    print(f'processed {ticker}')

# II batch 
for i,ticker in enumerate(tickers.values[200:400]):
    time.sleep(np.random.randint(5,7))
        
    # because we are working with the list of lists
    ticker = ticker[0]

    # check if ticker exists        
    input_df = df_all.loc[df_all['Ticker']==ticker].copy()
    print(f'len: {len(input_df)}, ticker: {ticker}, progress: {i+1}/{len(tickers.values)}')

    if len(input_df)<50:
        print(f'{ticker} not enough data')
        continue
    
    df, BS, RZiS, CF = map_financial_data(df = df_all.loc[df_all['Ticker']==ticker], db_conn = conn)
        
    if type(df)!=str:
        df.to_sql(str(ticker),schema='gpw_predictors',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} df')
        
    if type(BS)!=str:
        BS.to_sql(str(ticker),schema='gpw_BS',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} BS')
        
    if type(RZiS)!=str:
        RZiS.to_sql(str(ticker),schema='gpw_RZiS',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} RZiS')
        
    if type(CF)!=str:
        CF.to_sql(str(ticker),schema='gpw_CF',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} CF')
        continue


    print(f'processed {ticker}')

# III batch 
for i,ticker in enumerate(tickers.values[400:]):
    time.sleep(np.random.randint(5,7))
        
    # because we are working with the list of lists
    ticker = ticker[0]

    # check if ticker exists        
    input_df = df_all.loc[df_all['Ticker']==ticker].copy()
    print(f'len: {len(input_df)}, ticker: {ticker}, progress: {i+1}/{len(tickers.values)}')

    if len(input_df)<50:
        print(f'{ticker} not enough data')
        continue
    
    df, BS, RZiS, CF = map_financial_data(df = df_all.loc[df_all['Ticker']==ticker], db_conn = conn)
        
    if type(df)!=str:
        df.to_sql(str(ticker),schema='gpw_predictors',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} df')
        
    if type(BS)!=str:
        BS.to_sql(str(ticker),schema='gpw_BS',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} BS')
        
    if type(RZiS)!=str:
        RZiS.to_sql(str(ticker),schema='gpw_RZiS',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} RZiS')
        
    if type(CF)!=str:
        CF.to_sql(str(ticker),schema='gpw_CF',if_exists='replace',con=conn)
    else:
        print(f'ignoring {ticker} CF')
        continue


    print(f'processed {ticker}')