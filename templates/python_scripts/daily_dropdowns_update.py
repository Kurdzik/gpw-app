import sqlalchemy
import pandas as pd
import shutil
import os

conn_string = os.environ['DB_CONN_STRING']

engine = sqlalchemy.create_engine(conn_string)
conn = engine.connect()

q = f"""select distinct * from gpw.notowania"""
df = pd.read_sql(q,con=conn)

dates_list = []
for date in pd.to_datetime(df['Date'],format="%d-%m-%Y").sort_values().unique().astype(str):
    dates_list.append(date[:10])
   
# Updae dates dropdowns
with open('../static/dropdown/dates_to.csv','w') as file:
    for line in dates_list:
        file.write(line + ',')
        file.write('\n')

shutil.copy('../static/dropdown/dates_to.csv','../static/dropdown/dates_from.csv')

# Update prediction tickers dropdown
with open('../static/dropdown/tickers_preds.csv','w') as file:
    for line in ['ALL'] + df['Ticker'].unique().tolist():
        file.write(line + ',')
        file.write('\n')

# Update tickers dropdown
with open('../static/dropdown/tickers.csv','w') as file:
    for line in ['ALL'] + df['Ticker'].unique().tolist():
        file.write(line + ',')
        file.write('\n')

# Clear downloads
path = '../static/downloads/'
if len(os.listdir(path))>0:
    for file in os.listdir(path):
        os.remove(path + file)

