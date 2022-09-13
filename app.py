from flask import Flask,render_template, request
from templates.python_scripts.db_functions import get_data_from_db, test_db_conn
import pandas as pd
import sqlalchemy

download_ready = ''
approval = False
conn_string = ''
db_table = ''
db_schema = ''

app = Flask(__name__,template_folder='./templates',static_folder='./templates/static')

@app.route('/')
def main():

    return render_template('index.html')


#----------------- RAW DATA DOWNLOAD --------------------------------------------------------
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

#----------------- ANALYTICS MODULE --------------------------------------------------------
@app.route('/analytics')
def init_model():

    return render_template('index_analytics.html')

#----------------- CONNECT WITH EXTERNAL DB MODULE --------------------------------------------------------
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

    # message =1
    # message_link =2
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
                                                # ,


@app.route('/add_connection',methods=['POST','GET'])
def add_conn():

    # conn = sqlite3.connect('templates/static/db_credentials/creds_DB.db')
    engine = sqlalchemy.create_engine("postgresql://j341:ED1F_a359b0@psql01.mikr.us:5432/db_j341")
    conn = engine.connect()
    
    try:pd.DataFrame([conn_string,db_table,db_schema,'active']).T.rename({0:'connection_string',1:'table',2:'schema',3:'status'},axis=1).to_sql('connections',if_exists='append',con=conn,schema='connected_dbs',index=False)
    except Exception: print('error')
    message = 'Connection Added Successfully'


    return render_template('index_db_conn.html',message=message)


if __name__ == '__main__':
    app.run(debug=True)