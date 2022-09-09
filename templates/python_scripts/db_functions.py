import pandas as pd
from sqlalchemy import create_engine

def get_data_from_db(date_from,date_to,ticker):
       
    day_from = date_from[:2]
    month_from = date_from[3:5]
    year_from = date_from[-4:]
    
    day_to = date_to[:2]
    month_to = date_to[3:5]
    year_to = date_to[-4:]

    engine = create_engine("mysql+pymysql://test_user:Kolesgit99!@192.168.88.199:3307/GPW?charset=utf8mb4")
    conn = engine.connect()


    q = f"""select * from notowania where Date_new > '{year_from}-{month_from}-{day_from}' and Date_new <= '{year_to}-{month_to}-{day_to}' """

    df = pd.read_sql(q,con=conn).drop(columns=['level_0','index'])


    if ticker=='ALL':
        return df
        
    else:
        return df.loc[df['Ticker'].str.contains(ticker)]


def test_db_conn(db_type,db_user,db_pass,db_ip,db_port,database):

    if db_type=='PostgreSQL':
        conn_string = f"""postgresql://{db_user}:{db_pass}@{db_ip}:{db_port}/{database}"""      

    elif db_type=='MySQL' or db_type=='MariaDB':
        conn_string = f"""mysql+pymysql://{db_user}:{db_pass}@{db_ip}:{db_port}/{database}"""
    
    elif db_type=='Oracle':
        conn_string = f"""oracle://{db_user}:{db_pass}@{db_ip}:{db_port}/{database}"""

    elif db_type=='SQL Server':
        conn_string = f"""mssql+pymssql://{db_user}:{db_pass}@{db_ip}:{db_port}/{database}"""
        
    try:
        engine = create_engine(conn_string)
        engine.connect()
        msg = 'Connected!'
        msg_link = ''
        approval = True        
        return msg, msg_link, conn_string, approval

    except Exception:
        msg = 'Check your db credentials'
        msg_link = 'https://docs.sqlalchemy.org/en/14/core/engines.html'
        approval = False
        return  msg, msg_link, conn_string, approval
