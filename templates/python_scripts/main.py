from sqlalchemy import create_engine
engine = create_engine("postgresql://j341:ED1F_a359b0@psql01.mikr.us:5432/db_j341")
conn = engine.connect()

from gpw_functions import map_financial_data,get_stock_prices
df = get_stock_prices(date_from='16-09-2022',date_to='16-09-2022')

map_financial_data(df,conn)
