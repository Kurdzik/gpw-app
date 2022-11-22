from .constants import MODELS_FIRST_PART,MODELS_LAST_PART, PREDICTIONS_FIRST_PART, PREDICTIONS_LAST_PART
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.tools import diff
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.arima.model import ARIMA
import plotly.express as px
import pandas as pd
import os
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from sqlalchemy import create_engine
import mlflow
from tqdm import tqdm
from datetime import date
import warnings
warnings.filterwarnings('ignore')

tracking_uri = os.environ['MLFLOW_TRACKING_URI']
conn_string = os.environ['DB_CONN_STRING']
engine = create_engine(conn_string)
conn = engine.connect()

def select_ARMA(data):

    p = 1
    q = 1

    # Grid search for optimal p and q values (AR and MA parts)
    AIC_list_ARMA = []
    order_list_ARMA = []

    for p in tqdm(np.arange(start=0,stop=6)):
        for q in np.arange(start=0,stop=6):

            # for ARMA models
            model = ARIMA(data,order=(p,0,q)).fit()
            AIC_list_ARMA.append(model.aic)
            order_list_ARMA.append((p,0,q))

    # gather results in one df
    results = pd.DataFrame(data=AIC_list_ARMA, columns=['AIC_ARMA'])
    results['order_ARMA'] = order_list_ARMA

    # best ARMA
    ARMA_params = results.loc[results['AIC_ARMA']==results['AIC_ARMA'].min()]['order_ARMA'].values[0]
    ARMA_model = ARIMA(data,order=ARMA_params).fit()

    return ARMA_model

def select_ARIMA(data):

    def stationarity_check(series,_plot_acf=False):
        """
        Checks for series stationarity, and returns the lowest value of differences fow which series is stationary
        
        """

        for i in np.arange(start=1,stop=10):
            series_new = diff(series,k_diff=i)
            p_value = adfuller(series_new)[1]
            if p_value < 0.05:
                if _plot_acf:
                    print(f'{np.round(p_value,5)}, stationary for {i} differences')
                    plot_acf(series_new);
                return i

            else:
                if _plot_acf:
                    plot_acf(series_new);

    p = 1
    d = stationarity_check(series=data)
    q = 1

    # Grid search for optimal p and q values (AR and MA parts)
    AIC_list_ARIMA = []
    order_list_ARIMA = []

    for p in tqdm(np.arange(start=0,stop=6)):
        for q in np.arange(start=0,stop=6):

            # for ARIMA models
            model = ARIMA(data,order=(p,d,q)).fit()
            AIC_list_ARIMA.append(model.aic)
            order_list_ARIMA.append((p,d,q))

    # gather results in one df
    results = pd.DataFrame(data=AIC_list_ARIMA, columns=['AIC_ARIMA'])
    results['order_ARIMA'] = order_list_ARIMA

    # best ARIMA
    ARIMA_params = results.loc[results['AIC_ARIMA']==results['AIC_ARIMA'].min()]['order_ARIMA'].values[0]
    ARIMA_model = ARIMA(data,order=ARIMA_params).fit()

    return ARIMA_model

def train_and_register_model(model_name,dataset,ticker,tracking_uri):

    def eval_metrics(actual, pred):
        rmse = np.round(np.sqrt(mean_squared_error(actual, pred)),2)
        mae = np.round(mean_absolute_error(actual, pred),2)
        mape = np.round(mean_absolute_percentage_error(actual, pred)*100,2)
        return rmse, mae, mape

    if 'Holt' in model_name:
        try:
            model = ExponentialSmoothing(dataset,trend='mul',seasonal='mul',seasonal_periods=12).fit()
            preds = model.fittedvalues
        except Exception:
            return 1

    if 'ARMA' in model_name:
        try:
            model = select_ARMA(data=dataset)
            preds = model.fittedvalues
        except Exception:
            return 1
    
    if 'ARIMA' in model_name:
        try:
            model = select_ARIMA(data=dataset)
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

def load_model_and_plot(ticker,model_name,plot_last_mnths,conn,data_type='plot'):

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

    # Dataset parameters
    plot_data_since = pd.date_range(end=df.index.max(),periods=plot_last_mnths,freq='M')[0].date()

    mlflow.set_tracking_uri(tracking_uri)

    # MODEL SELECTION
    # ======================================================================================================================
    # MODEL 1 - Holt Winters - Exponential Smoothing
    if 'Holt' in model_name:
        model_version = f'Holt-Winters_{ticker}/1'
    
    # ======================================================================================================================
    # MODEL 2 - ARMA
    if 'ARMA' in model_name:
        model_version = f'ARMA_{ticker}/1'

    # ======================================================================================================================
    # MODEL 3 - ARIMA
    if 'ARIMA' in model_name:
        model_version = f'ARIMA_{ticker}/1'

    model = mlflow.statsmodels.load_model(f'models:/{model_version}')

    # Get fitted values from the model    
    fitted_data = model.fittedvalues

    # Get last date from fittedvalues and trim dataset to that date in order to plot and evaluate it
    last_date = fitted_data.tail(1).index.date[0]
    dataset = dataset[:last_date]
    
    # GRAPHS
    # ======================================================================================================================
    # Join data 
    joint_data = pd.concat([   
                            fitted_data.to_frame().rename({0:'Predictions','predicted_mean':'Predictions'},axis=1),
                            dataset.to_frame().rename({'Close':'True Value'},axis=1)
                            ],axis=1)

    joint_data = joint_data[plot_data_since:]

    # instantiate fig object
    fig_1 = px.line()

    # plot true data
    fig_1.add_scatter(x=joint_data.index, y=joint_data['True Value'], mode='lines',name='True Values')

    # plot predictions
    fig_1.add_scatter(x=joint_data.index, y=joint_data['Predictions'], mode='lines',name='Predictions')

    fig_1.update_layout(
        title=f'company: {ticker}, model: {model_name}',
        xaxis_title="Date",
        yaxis_title="Price in PLN"
    )

    # METRICS
    # ======================================================================================================================

    mape = mean_absolute_percentage_error(joint_data['True Value'],joint_data['Predictions']) 
    mae = mean_absolute_error(joint_data['True Value'],joint_data['Predictions']) 

    metrics = pd.DataFrame()
    
    metrics['Metric'] = ['Mean Absolute Percentage Error', 'Mean Absolute Error']
    metrics['Score'] = [f'{np.round(mape,4)*100} %', f'{np.round(mae,2)} PLN']

    metrics_html = metrics.to_html(index=False,justify='justify-all',col_space=250) + '<br>' + '<hr>'

    if data_type == 'html':
        full_html = MODELS_FIRST_PART + metrics_html + fig_1.to_html()[55:-15] + '<hr>' +  MODELS_LAST_PART
        
        return full_html

    elif data_type == 'plot':

        return fig_1.show(), metrics

def predict_and_plot(ticker,model_name,fcst_period,plot_last_mnths,conn,data_type):

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

    # Dataset parameters
    plot_data_since = pd.date_range(end=df.index.max(),periods=plot_last_mnths,freq='M')[0].date()

    mlflow.set_tracking_uri(tracking_uri)

    # MODEL SELECTION
    # ======================================================================================================================
    # MODEL 1 - Holt Winters - Exponential Smoothing
    if 'Holt' in model_name:
        model_version = f'Holt-Winters_{ticker}/1'
    
    # ======================================================================================================================
    # MODEL 2 - ARMA
    if 'ARMA' in model_name:
        model_version = f'ARMA_{ticker}/1'

    # ======================================================================================================================
    # MODEL 3 - ARIMA
    if 'ARIMA' in model_name:
        model_version = f'ARIMA_{ticker}/1'

    model = mlflow.statsmodels.load_model(f'models:/{model_version}')


    # Offset forecast period by the days that already passed between model training nad actual date
    now = str(date.today())
    last_day_known_to_model = str(model.fittedvalues.tail(1).index.date[0])

    forceast_offset = len(pd.date_range(start=last_day_known_to_model,end=now,freq='M')) + 1

    fcst_period += forceast_offset
    
    # Get index for forcated values - only Business Days, no weekends
    fcsted_index = pd.date_range(start=model.fittedvalues.index[-1],freq='B',periods=fcst_period)

    # Get forcasted values 
    fcsted_vals = model.forecast(fcst_period).to_frame().set_index(fcsted_index).rename({0:'Close','predicted_mean':'Close'},axis=1)

    # Merge historical and forecasted values into one data frame
    hist_data = dataset.to_frame()
    hist_data['Type'] = 'True Values'
    fcsted_vals['Type'] = 'Predictions'

    joint_data = pd.concat([hist_data,fcsted_vals],axis=0)[plot_data_since:]

    # GRAPHS
    # ======================================================================================================================
    fig = px.line(x=joint_data.index, y=joint_data['Close'], color = joint_data['Type'])

    fig.update_layout(
        title=f'company: {ticker}, model: {model_name}, prediction for: {fcst_period} days',
        xaxis_title="Date",
        yaxis_title="Price in PLN"
    )
    
    if data_type == 'html':
        full_html = PREDICTIONS_FIRST_PART + fig.to_html()[55:-15] +  PREDICTIONS_LAST_PART
        
        return full_html

    elif data_type == 'plot':

        return fig.show()