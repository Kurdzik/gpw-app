from statsmodels.tsa.holtwinters import ExponentialSmoothing
import plotly.express as px
from .constants import MODELS_FIRST_PART,MODELS_LAST_PART
import pandas as pd
import os
from statsmodels.tsa.arima.model import ARIMA

from sqlalchemy import create_engine
conn_string = os.environ['DB_CONN_STRING']
engine = create_engine(conn_string)
conn = engine.connect()


def predict_and_plot(forecst_periods,forecast_from,plot_last_mnths,model,ticker,data_type='plot'):

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
    plot_data_since = pd.date_range(end=forecast_from,periods=plot_last_mnths,freq='M')[0].date()

    # Train test split
    train = df[:forecast_from]['Close']
    test = df[forecast_from:]['Close']





    # MODEL SELECTION
    # ======================================================================================================================
    # MODEL 1 - Holt Winters - Exponential Smoothing
    if model == 'Holt-Winters - Exponential Smoothing Model':
        model = ExponentialSmoothing(train,trend='mul',seasonal='mul',seasonal_periods=12).fit()
        preds = model.forecast(forecst_periods)

    # MODEL 2 - ARIMA
    if model == 'ARIMA':
        model = ARIMA(df['Close'], order=(1, 0, 24)).fit()
        preds = model.forecast(forecst_periods)

    else:
        return MODELS_FIRST_PART + 'Model not ready' + MODELS_LAST_PART


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
        return full_html

    elif data_type == 'plot':
        return fig.show()