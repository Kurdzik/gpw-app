import os
from datetime import date

import pandas as pd
from gpw_functions import get_stock_prices
from sqlalchemy import create_engine

conn_string = os.environ["DB_CONN_STRING"]
engine = create_engine(conn_string)
conn = engine.connect()


def day():
    if date.today().day < 10:
        return "0" + str(date.today().day)
    else:
        return str(date.today().day)


def month():
    if date.today().month < 10:
        return "0" + str(date.today().month)
    else:
        return str(date.today().month)


def year():
    if date.today().year < 10:
        return "0" + str(date.today().year)
    else:
        return str(date.today().year)


# Get date in a correct format
stocs_date = f"{day()}-{month()}-{year()}"

# Get stock prices for that date
data = get_stock_prices(stocs_date, stocs_date)
if len(data) > 0:
    # Get all registered connection stirings

    creds = pd.read_sql("select * from connected_dbs.connections", con=conn)

    # Iterate through conn strings and upload the data
    for conn_string in creds.iterrows():
        try:
            data.to_sql(
                conn_string[1][1],
                con=conn_string[1][0],
                schema=conn_string[1][2],
                if_exists="append",
            )
            print(f"data uploaded to {conn_string}")
        except Exception:
            print(f"data could not be loaded uploaded to {conn_string}")
            continue

else:
    print("No records collected today")
