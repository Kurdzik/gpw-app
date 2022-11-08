import sqlalchemy
import os
import sqlalchemy
import warnings
import pandas as pd 
from tqdm import tqdm
from .models import train_and_register_model
warnings.filterwarnings('ignore')

conn_string = os.environ['DB_CONN_STRING']
engine = sqlalchemy.create_engine(conn_string)
conn = engine.connect()

q1 = f'''
SELECT DISTINCT "Ticker"
FROM gpw.notowania'''

# Get All Tickers
tickers = pd.read_sql(q1,conn)
tickers = tickers.Ticker.tolist()

for ticker in tqdm(tickers):

    q = f'''
    SELECT "Close","Date"
    FROM gpw.notowania
    where "Ticker" = '{ticker}'
    order by to_date("Date",'dd-mm-yyyy'); '''

    # Get Data
    df = pd.read_sql(q,conn)

    # Preprocess
    df['Date'] = pd.to_datetime(df['Date'],dayfirst=True)
    df = df.set_index('Date')
    df['Close'] = df['Close'].astype(float)
    dataset = df['Close']

    # Iterate through models, train them and register to mlflow
    for _model_name in ['Holt-Winters','ARMA','ARIMA']:    

        res = train_and_register_model(model_name=_model_name,
                                       dataset=dataset,
                                       ticker=ticker,
                                       tracking_uri='http://localhost:5000')
        if res == 1:
            print('model for',ticker,'could not be logged')
            continue