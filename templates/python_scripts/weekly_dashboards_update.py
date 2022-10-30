import sqlalchemy
import pandas as pd
import os
from gpw_functions import map_financial_data
import time
import numpy as np
import time
import warnings
from tqdm import tqdm

warnings.filterwarnings("ignore")

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


for ticker in tqdm(tickers.values[495:]):
    time.sleep(np.random.randint(5,7))
        
    # because we are working with the list of lists
    ticker = ticker[0]

    # check if ticker exists        
    input_df = df_all.loc[df_all['Ticker']==ticker].copy()
    print(f'len: {len(input_df)}, ticker: {ticker}')

    if len(input_df)<50:
        print(f'{ticker} not enough data')
        continue
    
    df, BS, RZiS, CF = map_financial_data(df = df_all.loc[df_all['Ticker']==ticker], db_conn = conn)
    
    if type(df)!=str:
        try: 
            df.drop(columns='level_0',inplace=True)
        except Exception:
            pass

        df.to_sql(ticker,schema='gpw_predictors',if_exists='replace',con=conn)
        print('uploaded df')
    else:
        print(f'ignoring {ticker} df')
        
    if type(BS)!=str:
        try: 
            BS.drop(columns='level_0',inplace=True)
        except Exception:
            pass
        BS.to_sql(ticker,schema='gpw_BS',if_exists='replace',con=conn)
        print('uploaded BS')
    else:
        print(f'ignoring {ticker} BS')
        
    if type(RZiS)!=str:
        try: 
            RZiS.drop(columns='level_0',inplace=True)
        except Exception:
            pass
        RZiS.to_sql(ticker,schema='gpw_RZiS',if_exists='replace',con=conn)
        print('uploaded RZiS')
    else:
        print(f'ignoring {ticker} RZiS')
        
    if type(CF)!=str:
        try: 
            CF.drop(columns='level_0',inplace=True)
        except Exception:
            pass
        CF.to_sql(ticker,schema='gpw_CF',if_exists='replace',con=conn)
        print('uploaded CF')
    else:
        print(f'ignoring {ticker} CF')
        continue


    print(f'processed {ticker}')


    