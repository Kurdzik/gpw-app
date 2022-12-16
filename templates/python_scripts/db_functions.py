import pandas as pd
from sqlalchemy import create_engine
import os

conn_string = os.environ["DB_CONN_STRING"]

engine = create_engine(conn_string)
conn = engine.connect()


def get_data_from_db(date_from, date_to, ticker):

    date_from = str(date_from)
    date_to = str(date_to)

    day_from = date_from[-2:]
    month_from = date_from[5:7]
    year_from = date_from[:4]

    day_to = date_to[-2:]
    month_to = date_to[5:7]
    year_to = date_to[:4]

    # q = f"""select * from gpw.notowania where Date > '{year_from}-{month_from}-{day_from}' and Date <= '{year_to}-{month_to}-{day_to}' """

    q = f""" SELECT "index", "Ticker", "Currency", "Open", "Max", "Min", "Close", "Volume_in_thousands","Date"
             FROM gpw.notowania
             where TO_DATE("Date",'DD-MM-YYYY') >= '{year_from}-{month_from}-{day_from}' and TO_DATE("Date",'DD-MM-YYYY') <= '{year_to}-{month_to}-{day_to}'
             ORDER BY "Date" ASC ;"""

    df = pd.read_sql(q, con=conn).drop(columns=["index"])

    if ticker == "ALL":
        return df

    else:
        return df.loc[df["Ticker"].str.contains(ticker)]


def test_db_conn(db_type, db_user, db_pass, db_ip, db_port, database):

    if db_type == "PostgreSQL":
        conn_string = (
            f"""postgresql://{db_user}:{db_pass}@{db_ip}:{db_port}/{database}"""
        )

    elif db_type == "MySQL" or db_type == "MariaDB":
        conn_string = (
            f"""mysql+pymysql://{db_user}:{db_pass}@{db_ip}:{db_port}/{database}"""
        )

    elif db_type == "Oracle":
        conn_string = f"""oracle://{db_user}:{db_pass}@{db_ip}:{db_port}/{database}"""

    elif db_type == "SQL Server":
        conn_string = (
            f"""mssql+pymssql://{db_user}:{db_pass}@{db_ip}:{db_port}/{database}"""
        )

    try:
        engine = create_engine(conn_string)
        engine.connect()
        msg = "Connected!"
        msg_link = ""
        approval = True
        return msg, msg_link, conn_string, approval

    except Exception:
        msg = "Check your db credentials"
        msg_link = "https://docs.sqlalchemy.org/en/14/core/engines.html"
        approval = False
        return msg, msg_link, conn_string, approval
