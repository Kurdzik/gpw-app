import sqlalchemy
import os
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
import sqlalchemy
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima import ARIMA
import warnings
import mlflow
import numpy as np
import pandas as pd 
warnings.filterwarnings('ignore')

conn_string = os.environ['DB_CONN_STRING']
engine = sqlalchemy.create_engine(conn_string)
conn = engine.connect()

def train_and_register_model(model_name,dataset,ticker,tracking_uri):

    def eval_metrics(actual, pred):
        rmse = np.round(np.sqrt(mean_squared_error(actual, pred)),2)
        mae = np.round(mean_absolute_error(actual, pred),2)
        mape = np.round(mean_absolute_percentage_error(actual, pred)*100,2)
        return rmse, mae, mape


    if 'Holt' in model_name:

        # Training
        try:
            model = ExponentialSmoothing(dataset,trend='mul',seasonal='mul',seasonal_periods=12).fit()
            preds = model.fittedvalues
        except Exception:
            return 1

    # Setting up mlflow connection
    mlflow.set_tracking_uri(tracking_uri)

    # Setting experiment
    experiment = mlflow.set_experiment(ticker)
  
    with mlflow.start_run(experiment_id=experiment.experiment_id,run_name=model_name):
    
        rmse, mae, mape = eval_metrics(dataset,preds)
        
        mlflow.log_param("RMSE", rmse)
        mlflow.log_param("MAE", mae)
        mlflow.log_param("MAPE", mape)
         
        # Logging model
        mlflow.sklearn.log_model(model, "model", registered_model_name=f'{model_name}_{ticker}')
        print('model logged for',f'{model_name}_{ticker}')


q1 = f'''
SELECT DISTINCT "Ticker"
FROM gpw.notowania'''

# Get All Tickers
tickers = pd.read_sql(q1,conn)
tickers = tickers.Ticker.tolist()

for ticker in tickers:

    q = f'''
    SELECT "Close","Date"
    FROM gpw.notowania
    where "Ticker" = '{ticker}'
    order by to_date("Date",'dd-mm-yyyy'); '''

    # Get Data
    df = pd.read_sql(q,conn)
    print('data gathered')

    # Preprocess
    df['Date'] = pd.to_datetime(df['Date'],dayfirst=True)
    df = df.set_index('Date')
    df['Close'] = df['Close'].astype(float)
    dataset = df['Close']

    print('data preprocessed')
    
    res = train_and_register_model(model_name='Holt-Winters',
                            dataset=dataset,
                            ticker=ticker,
                            tracking_uri='http://localhost:5000')
    if res == 1:
        print('model for',ticker,'could not be logged')
        continue