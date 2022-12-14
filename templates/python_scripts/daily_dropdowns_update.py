import os
import shutil

import pandas as pd
import sqlalchemy

conn_string = os.environ["DB_CONN_STRING"]

engine = sqlalchemy.create_engine(conn_string)
conn = engine.connect()

q = f"""select distinct * from gpw.notowania"""
df = pd.read_sql(q, con=conn)

dates_list = []
for date in (
    pd.to_datetime(df["Date"], format="%d-%m-%Y").sort_values().unique().astype(str)
):
    dates_list.append(date[:10])

# Updae dates dropdowns
with open("../static/dropdown/dates_to.csv", "w") as file:
    for line in reversed(dates_list):
        file.write(line + ",")
        file.write("\n")

shutil.copy("../static/dropdown/dates_to.csv", "../static/dropdown/dates_from.csv")

# Update prediction tickers dropdown
q_1 = """SELECT distinct "Ticker" FROM gpw.notowania;"""
df_all_tickers = pd.read_sql(q_1, conn)

list_of_existing_tickers = []

for ticker in list(df_all_tickers["Ticker"]):

    q_2 = f"""SELECT * FROM gpw_predictors."{ticker}"
    order by to_date("Date",'dd-mm-yyyy');"""

    try:
        df_if_exist = pd.read_sql(q_2, conn)
        if len(df_if_exist) > 0:
            list_of_existing_tickers.append(ticker)
    except Exception:
        continue

with open("../static/dropdown/tickers_preds.csv", "w") as file:
    for line in pd.Series(list_of_existing_tickers).sort_values().to_list():
        file.write(line + ",")
        file.write("\n")

# Update tickers dropdown
with open("../static/dropdown/tickers.csv", "w") as file:
    for line in ["ALL"] + df["Ticker"].unique().tolist():
        file.write(line + ",")
        file.write("\n")

# Clear downloads
path = "../static/downloads/"
if len(os.listdir(path)) > 0:
    for file in os.listdir(path):
        if ".gitkeep" != file:
            os.remove(path + file)
