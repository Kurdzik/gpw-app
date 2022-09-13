from gpw_functions import get_stock_prices
from datetime import date
import sqlite3

import pandas as pd
from sqlalchemy import create_engine
engine = create_engine("postgresql://j341:ED1F_a359b0@psql01.mikr.us:5432/db_j341")
conn = engine.connect()

def day():
    if date.today().day<10:
        return '0' + str(date.today().day)
    else:
        return str(date.today().day)

def month():
    if date.today().month<10:
        return '0' + str(date.today().month)
    else:
        return str(date.today().month)
    
def year():
    if date.today().year<10:
        return '0' + str(date.today().year)
    else:
        return str(date.today().year)

# Get date in a correct format
stocs_date = f'{day()}-{month()}-{year()}'

# Get stock prices for that date
data = get_stock_prices(stocs_date,stocs_date)

# Get all registered connection stirings
conn_creds = sqlite3.connect('../static/db_credentials/creds.db')
creds = pd.read_sql('select * from connections', con=conn_creds)

# Iterate through conn strings and upload the data
for conn_string in creds.iterrows():
    try:
        print('table',conn_string[1][1])
        print('conn str', conn_string[1][0])
        print('schema',conn_string[1][2])
        # data.to_sql(conn_string[1][1],con = conn_string[1][0], schema = conn_string[1][2],if_exists = 'append')
        # print('Data uploaded succesfully')
    except Exception:
        # print('Error during data upload')
        continue
    