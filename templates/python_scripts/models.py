from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.express as px
from .constants import MODELS_FIRST_PART,MODELS_LAST_PART, PREDICTIONS_FIRST_PART, PREDICTIONS_LAST_PART
import pandas as pd
import os
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error, mean_absolute_error
import plotly.graph_objects as go

import warnings
warnings.filterwarnings('ignore')

from sqlalchemy import create_engine
conn_string = os.environ['DB_CONN_STRING']
engine = create_engine(conn_string)
conn = engine.connect()


def fit_and_plot(ticker,model_name,plot_last_mnths,conn,data_type='plot'):

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


    # MODEL SELECTION
    # ======================================================================================================================
    # MODEL 1 - Holt Winters - Exponential Smoothing
    if 'Holt' in model_name:
        model = ExponentialSmoothing(dataset,trend='mul',seasonal='mul',seasonal_periods=12).fit()


    fitted_data = model.fittedvalues



    # GRAPHS
    # ======================================================================================================================
    # Join data 
    joint_data = pd.concat([   
                            fitted_data.to_frame().rename({0:'Predictions'},axis=1),
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

    # fig_2 = go.Figure(data=[go.Table(header=dict(values=['Metric', 'Score']),
    #                 cells=dict(values=[['Mean Absolute Percentage Error', 'Mean Absolute Error'], [f'{np.round(mape,4)*100} %', f'{np.round(mae,2)} PLN']]))
    #                     ])
    # fig_2.update_layout(
    #     height=250        
    # )

    metrics = pd.DataFrame()
    
    metrics['Metric'] = ['Mean Absolute Percentage Error', 'Mean Absolute Error']
    metrics['Score'] = [f'{np.round(mape,4)*100} %', f'{np.round(mae,2)} PLN']

    metrics_html = metrics.to_html(index=False,justify='justify-all',col_space=250) + '<br>' + '<hr>'

    if data_type == 'html':
        full_html = MODELS_FIRST_PART + metrics_html + fig_1.to_html()[55:-15] + '<hr>' +  MODELS_LAST_PART
        
        return full_html

    elif data_type == 'plot':

        return fig_1.show() + metrics



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


    # MODEL SELECTION
    # ======================================================================================================================
    # MODEL 1 - Holt Winters - Exponential Smoothing

    if 'Holt' in model_name:
        model = ExponentialSmoothing(dataset,trend='mul',seasonal='mul',seasonal_periods=12).fit()


    # Get index for forcated values - only Business Days, no weekends
    fcsted_index = pd.date_range(start=model.fittedvalues.index[-1],freq='B',periods=fcst_period)

    # Get forcasted values 
    fcsted_vals = model.forecast(fcst_period).to_frame().set_index(fcsted_index).rename({0:'Close'},axis=1)

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