from flask import Flask,render_template, request
from templates.python_scripts.db_functions import get_data_from_db, test_db_conn
import pandas as pd
import sqlalchemy
import os

conn_string = os.environ['DB_CONN_STRING']

engine = sqlalchemy.create_engine(conn_string)
conn = engine.connect()

download_ready = ''
approval = False
conn_string = ''
db_table = ''
db_schema = ''

app = Flask(__name__,template_folder='./templates',static_folder='./templates/static')

#----------------- HOME PAGE -------------------------------------------------------------------------------
@app.route('/')
def main():

    return render_template('index.html')


#----------------- RAW DATA DOWNLOAD -----------------------------------------------------------------------
@app.route('/get_data')
def init_data_loader():
    global download_ready

    download_ready = ''

    return render_template('index_scrapper.html',download_ready=download_ready)

@app.route('/get_data_from_db',methods=['POST','GET'])
def run_data_loader():
    global download_ready

    ticker = request.form['tickerSelection']
    date_from = request.form['Dates1Selection']
    date_to = request.form['Dates2Selection']

    df = get_data_from_db(date_from=date_from,
                     date_to=date_to,
                     ticker=ticker)

    file_name = 'stocks_'+date_from+'-'+date_to+'.csv'

    df.to_csv(f'templates/static/downloads/{file_name}',index=False)

    download_ready = 'Click here to download'
      
    return render_template('index_scrapper.html',download_ready=download_ready,file_name=file_name)

#----------------- CONNECT WITH EXTERNAL DB MODULE --------------------------------------------------------
@app.route('/db_choice')
def init_db_choice():

    return render_template('index_db_conn_choice.html')

@app.route('/db_conn')
def init_conn():
    message = ''
    approval = False
    conn_string = ''
    add_record_button = ''
    
    return render_template('index_db_conn.html',message=message,add_record_button=add_record_button), approval, conn_string

@app.route('/connection',methods=['POST','GET'])
def test_conn():
    global conn_string, db_table, db_schema

    db_type = request.form['selectDatabases']
    db_ip = request.form['DBIP']
    db_port = request.form['DBPort']
    database = request.form['DB']
    db_user = request.form['DBUser']
    db_pass = request.form['DBPass']
    db_table = request.form['Table']
    db_schema = request.form['Schema']
    add_record_button = ''
    wrong_conn_string = ''

    message, message_link, conn_string, approval = test_db_conn(db_type=db_type,
                                                                db_ip=db_ip,
                                                                db_port=db_port,
                                                                database=database,
                                                                db_user=db_user,
                                                                db_pass=db_pass)
    

    if approval:
        add_record_button = 'Click here to register your Database'
        message_link = ''
       
    elif not approval:
        message_link = message_link
        wrong_conn_string = conn_string
  

    return render_template('index_db_conn.html',message=message,
                                                message_link=message_link,
                                                wrong_conn_string=wrong_conn_string,
                                                add_record_button=add_record_button
                                                ),approval

@app.route('/add_connection',methods=['POST','GET'])
def add_conn():


    
    try:pd.DataFrame([conn_string,db_table,db_schema,'active']).T.rename({0:'connection_string',1:'table',2:'schema',3:'status'},axis=1).to_sql('connections',if_exists='append',con=conn,schema='connected_dbs',index=False)
    except Exception: message = 'Something went wrong, connection was not added'
    message = 'Connection added successfully'


    return render_template('index_db_conn.html',message=message)

@app.route('/find_existing_conn',methods=['POST','GET'])
def init_conn_removal():
    
    return render_template('index_db_conn_remove.html')

@app.route('/confirmation',methods=['POST','GET'])
def confirm_removal():
    global conn_string

    db_type = request.form['selectDatabases']
    db_ip = request.form['DBIP']
    db_port = request.form['DBPort']
    database = request.form['DB']
    db_user = request.form['DBUser']
    db_pass = request.form['DBPass']


    message, message_link, conn_string, approval = test_db_conn(db_type=db_type,
                                                                db_ip=db_ip,
                                                                db_port=db_port,
                                                                database=database,
                                                                db_user=db_user,
                                                                db_pass=db_pass)
    
    # conn = sqlite3.connect('templates/static/db_credentials/creds.db')
    q = 'select * from connected_dbs.connections'
    df = pd.read_sql(q,conn)

    if len(df.loc[df.connection_string==conn_string])==0:
        message = 'Connection not in a database'
    else:
        message = 'Connection found!'
    
    remove_record_button = 'Click here to remove your Database from registry'


    return render_template('index_db_conn_remove.html',message=message,remove_record_button=remove_record_button)

@app.route('/remove_conn',methods=['POST','GET'])
def remove_conn():
    global conn_string

    message = ''

    print('connection string:',conn_string)

    q = 'select * from connected_dbs.connections'
    df = pd.read_sql(q,conn)

    df = df.drop(df.loc[df.connection_string==conn_string].index)

    df.to_sql('connections',if_exists='replace',con=conn, schema='connected_dbs', index=False)

    message = 'Connection removed successfully'

    return render_template('index_db_conn_remove.html',message=message)

#----------------- ANALYTICS MODULE --------------------------------------------------------
@app.route('/analytics')
def init_analytics_choice():

    return render_template('index_analytics_choice.html')

@app.route('/analytics_forecasting')
def init_model():

    return render_template('index_analytics_models.html')

@app.route('/analytics_select_dashboards')
def init_fundam_analysis():

    return render_template('index_analytics_dashboards.html')

if __name__ == '__main__':
    app.run(debug=True)







    # import pandas as pd
    # import plotly
    # import json
    # import plotly.express as px
    # import chart_studio.tools as tls

    # if ticker != 'ALL':

    #     fig = px.line(df, x="Date", y="Close", title=ticker)
    #     # title = ticker+date_from+'-'+date_to
    #     # fig.write_html(f'{title}.html')
             
    #     fig_html = fig.to_html()[7:-8]
    #     # preview_table = df.to_html(justify='center')