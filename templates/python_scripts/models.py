from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.express as px
from .constants import MODELS_FIRST_PART,MODELS_LAST_PART
import pandas as pd
import os
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

import warnings
warnings.filterwarnings('ignore')

from sqlalchemy import create_engine
conn_string = os.environ['DB_CONN_STRING']
engine = create_engine(conn_string)
conn = engine.connect()


def predict_and_plot(split_proportion,model,ticker,data_type='plot'):

    plot_last_mnths = 3

    # Get data
    q_2 = f'''SELECT * FROM gpw_predictors."{ticker}"
    order by to_date("Date",'dd-mm-yyyy');'''

    # preprocess data
    df = pd.read_sql(q_2,conn)
    df['Close_pct'] = df['Close'].pct_change().mul(100)
    df['Open_pct'] = df['Open'].pct_change().mul(100)
    df['Max_pct'] = df['Max'].pct_change().mul(100)
    df['Min_pct'] = df['Min'].pct_change().mul(100)
    df = df.iloc[1:,:]
    df = df.drop(columns=['level_0','index','Ticker','Currency','Open','Max','Min','Year'])
    df['Date'] = pd.to_datetime(df['Date'],dayfirst=True)
    df = df.set_index('Date')

    # Dataset parameters
    plot_data_since = pd.date_range(end=df.index.min(),periods=plot_last_mnths,freq='M')[0].date()

    # Train test split
    split_size = int(len(df)*split_proportion)

    # if Y != None:
    # X_train,Y_train = X[:split_size],Y[:split_size]
    # X_test,Y_test = X[split_size:],Y[split_size:]

    train = df[:split_size]['Close']
    test = df[split_size:]['Close']
    forecst_periods = len(test)
    print('==========================================================')
    print('train',len(train),'test',len(test))
    print('==========================================================')
    print('Min:', df.index.max(),'Max:', df.index.max() )
    print('==========================================================')

    if len(test)<=1:
        return MODELS_FIRST_PART + '''Predictions into a future are not yet implemented, 
                                    \n please check model performance on historical data''' + MODELS_LAST_PART


    # MODEL SELECTION
    # ======================================================================================================================
    # MODEL 1 - Holt Winters - Exponential Smoothing
    if 'Holt' in model:
        model = ExponentialSmoothing(train,trend='mul',seasonal='mul',seasonal_periods=12).fit()
        preds = model.forecast(forecst_periods)

    print('Model trained')
    print('==========================================================')

    # MODEL 2 - ARIMA
    if model == 'ARIMA':
        model = ARIMA(df['Close'], order=(1, 0, 12)).fit()
        preds = model.forecast(forecst_periods)

    # MODEL 3 - SARIMAX
    if model == 'SARIMAX':
        model = SARIMAX(df['Close'], order=(1, 0, 12)).fit()
        preds = model.forecast(forecst_periods)


    # PLOTTING
    # ======================================================================================================================
    # convert preds from series to 
    df_preds = preds.to_frame()
    df_preds['Date'] = pd.date_range(train.index[-1],periods=forecst_periods);
    df_preds = df_preds.rename({0:'Close'},axis=1);
    df_preds = df_preds.set_index('Date');

    df_train = pd.DataFrame(train);

    joint = pd.concat([df_train,df_preds]);

    # predictions
    pred_data = joint['Close'].iloc[-forecst_periods-1:];

    # historical data
    hist_data = joint['Close'].iloc[:-forecst_periods];

    # true data 
    pred_idx = pred_data.to_frame().index;
    df_test = df['Close'].iloc[len(hist_data)-1 : len(hist_data)+forecst_periods].to_frame().set_index(pred_idx)['Close']

    # plot historical data
    fig = px.line(hist_data[plot_data_since:], x=hist_data[plot_data_since:].index, y='Close')

    # plot predictions
    fig.add_scatter(x=df_preds[plot_data_since:].index, y=df_preds[plot_data_since:].rename({'predicted_mean':'Close'},axis=1)['Close'], mode='lines',name='Predictions')

    # plot true data
    fig.add_scatter(x=df_test.to_frame()[plot_data_since:].index, y=df_test.to_frame()[plot_data_since:]['Close'], mode='lines',name='True data')
    

    if data_type == 'html':
        full_html = MODELS_FIRST_PART + fig.to_html()[55:-15] + MODELS_LAST_PART
        
        print('Plot generated')
        print('==========================================================')

        return full_html

    elif data_type == 'plot':

        print('Plot generated')
        print('==========================================================')
        return fig.show()