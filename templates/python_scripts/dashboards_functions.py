import os
import time

import numpy as np
import pandas as pd
import plotly.express as px
import tqdm
import unidecode
from plotly.subplots import make_subplots
from sqlalchemy import create_engine

from .constants import DASHBOARDS_FIRST_PART, DASHBOARDS_LAST_PART
from .gpw_functions import map_financial_data

conn_string = os.environ["DB_CONN_STRING"]
engine = create_engine(conn_string)
conn = engine.connect()


def get_and_plot_data(ticker, data_type="plot"):

    # DATA GATHERING
    # ================================================================================================================
    def convert_to_floats(df):
        for col in df.columns:
            try:
                df[col] = (
                    df[col]
                    .apply(unidecode.unidecode)
                    .apply(lambda x: x.replace(" ", ""))
                    .apply(float)
                )
            except Exception:
                continue

        return df

    # ================================================================================================================
    q_rzis = f"""SELECT *
    FROM "gpw_RZiS"."{ticker}";
    """
    try:
        df_rzis = (
            pd.read_sql(q_rzis, con=conn)
            .drop(columns="index")
            .rename({"O4K ": "2022", "Inde": "index"}, axis=1)
            .set_index("index")
            .T.reset_index()
        )
        df_rzis = convert_to_floats(df_rzis)
    except Exception:
        df_rzis = None
    # ================================================================================================================
    q_cf = f"""SELECT *
    FROM "gpw_CF"."{ticker}";
    """
    try:
        df_cf = (
            pd.read_sql(q_cf, con=conn)
            .drop(columns="index")
            .rename({"O4K ": "2022", "Inde": "index"}, axis=1)
            .set_index("index")
            .T.reset_index()
        )
        df_cf = convert_to_floats(df_cf)
    except Exception:
        df_cf = None
    # ================================================================================================================

    q_bs = f"""SELECT *
    FROM "gpw_BS"."{ticker}";
    """
    try:
        df_bs = (
            pd.read_sql(q_bs, con=conn)
            .drop(columns="index")
            .rename({"O4K ": "2022", "Inde": "index"}, axis=1)
            .set_index("index")
            .T.reset_index()
        )
        df_bs = convert_to_floats(df_bs)
        df_bs["Total liabilities"] = (
            df_bs["Aktywa razem"]
            - df_bs["Kapita?? w??asny akcjonariuszy jednostki dominuj??cej"]
            - df_bs["Kapita?? (fundusz) podstawowy"]
            - df_bs["Udzia??y (akcje) w??asne"]
            - df_bs["Kapita?? (fundusz) zapasowy"]
            - df_bs["Udzia??y niekontroluj??ce"]
        )
    except Exception:
        df_bs = None

    # ================================================================================================================
    q_pred = f"""SELECT *
    FROM "gpw_predictors"."{ticker}" order by TO_DATE("Date",'DD-MM-YYYY');
    """
    try:
        df_pred = pd.read_sql(q_pred, con=conn).drop(columns=["index", "level_0"])
        df_pred = convert_to_floats(df_pred)
    except Exception:
        df_pred = None

    # DATA PLOTTING
    # ================================================================================================================

    import plotly.graph_objects as go

    # ======== Profitability ================================================================================================================================================================================================
    # Graph 1 - (sales revenue) Przychody ze sprzeda??y vs (COGS) Techniczny koszt wytworzenia produkcji sprzedanej + Koszty sprzeda??y + Koszty og??lnego zarz??du
    try:
        fig1 = px.bar(
            data_frame=df_rzis.rename(
                {"Przychody ze sprzeda??y": "Sales Revenue", "Zysk netto": "Net Profit"},
                axis=1,
            ),
            y="Sales Revenue",
            x="index",
            text_auto=True,
        ).data[0]
    except Exception:
        fig1 = px.bar(x=[0], y=[0]).data[0]

    # Graph 2 - (net profit) Zysk netto
    try:
        fig2 = px.bar(
            data_frame=df_rzis.rename(
                {"Przychody ze sprzeda??y": "Sales Revenue", "Zysk netto": "Net Profit"},
                axis=1,
            ),
            y="Net Profit",
            x="index",
            color="Net Profit",
            text_auto=True,
        ).data[0]
    except Exception:
        fig2 = px.bar(x=[0], y=[0]).data[0]

    # ======== Liquidity ====================================================================================================================================================================================================
    # Graph 3 - (cash flow from operations) Przep??ywy pieni????ne z dzia??alno??ci operacyjnej
    try:
        fig3 = px.bar(
            data_frame=df_cf.rename(
                {
                    "Przep??ywy pieni????ne z dzia??alno??ci operacyjnej": "CF from operations",
                    "Przep??ywy pieni????ne razem": "Total CF",
                },
                axis=1,
            ),
            y="CF from operations",
            x="index",
            color="CF from operations",
            text_auto=True,
        ).data[0]
    except Exception:
        fig3 = px.bar(x=[0], y=[0]).data[0]

    # Graph 4 - (total cash flow) Przep??ywy pieni????ne razem
    try:
        fig4 = px.bar(
            data_frame=df_cf.rename(
                {
                    "Przep??ywy pieni????ne z dzia??alno??ci operacyjnej": "CF from operations",
                    "Przep??ywy pieni????ne razem": "Total CF",
                },
                axis=1,
            ),
            y="Total CF",
            x="index",
            color="Total CF",
            text_auto=True,
        ).data[0]
    except Exception:
        fig4 = px.bar(x=[0], y=[0]).data[0]

    # ======== Balance Sheet ================================================================================================================================================================================================
    # Graph 5 - (total assets) Aktywa razem
    try:
        fig5 = px.bar(
            data_frame=df_bs.rename({"Aktywa razem": "Total assets"}, axis=1),
            y="Total assets",
            x="index",
            text_auto=True,
        ).data[0]
    except Exception:
        fig5 = px.bar(x=[0], y=[0]).data[0]

    # Graph 6 - (total liabilities) Aktywa razem - Kapita?? w??asny akcjonariuszy jednostki dominuj??cej - Kapita?? (fundusz) podstawowy - Udzia??y (akcje) w??asne - Kapita?? (fundusz) zapasowy - Udzia??y niekontroluj??ce
    try:
        fig6 = px.bar(
            data_frame=df_bs, y="Total liabilities", x="index", text_auto=True
        ).data[0]
    except Exception:
        fig6 = px.bar(x=[0], y=[0]).data[0]

    # ======== Indicators ===================================================================================================================================================================================================
    # Graph 7 - (P/E) C/Z
    try:
        fig7 = px.line(
            data_frame=df_pred.rename({"C/Z": "P/E"}, axis=1), y="P/E", x="Date"
        ).data[0]
    except Exception:
        fig7 = px.bar(x=[0], y=[0]).data[0]

    # Graph 8 - (P/BW) C/WK
    try:
        fig8 = px.line(
            data_frame=df_pred.rename({"C/WK": "P/BV"}, axis=1), y="P/BV", x="Date"
        ).data[0]
    except Exception:
        fig8 = px.bar(x=[0], y=[0]).data[0]

    # Graph 9 - (EV/EBITDA) EV/EBITDA
    try:
        fig9 = px.line(data_frame=df_pred, y="EV / EBITDA", x="Date").data[0]
    except Exception:
        fig9 = px.bar(x=[0], y=[0]).data[0]

    # ======== Figures =====================================================================================================================================================================================================
    fig_list = [fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9]

    fig = make_subplots(
        rows=9,
        cols=1,
        subplot_titles=(
            "Sales Revenue",
            "Net Profit/Loss",
            "Cash flow from operations",
            "Total cash flow",
            "Total assets",
            "Total liabilities",
            "Price to Earnings indicator",
            "Price to Book Value indicator ",
            "Enterpise Value to EBITDA indicator",
        ),
    )
    for i, fig_ in enumerate(fig_list):
        fig.add_trace(fig_, row=i + 1, col=1)

    fig.update_layout(
        height=3000,
        width=1200,
        title_text="Financial data in PLN",
        coloraxis=dict(colorscale="temps_r"),
        paper_bgcolor="rgb(0,0,0,0)",
        font=dict(color="white"),
    )

    if data_type == "html":
        full_html = DASHBOARDS_FIRST_PART + fig.to_html()[55:-15] + DASHBOARDS_LAST_PART
        return full_html

    elif data_type == "plot":
        return fig.show()


def dashboards_update():

    # get all data
    q = f"""select distinct * from gpw.notowania """
    df_all = pd.read_sql(q, con=conn)

    # get all tickers
    q = f"""SELECT distinct "Ticker" FROM gpw.notowania order by "Ticker";"""
    tickers = pd.read_sql(q, con=conn)

    # upload the data on separate schemas if the data is avaiable

    for ticker in tqdm(tickers.values):
        time.sleep(np.random.randint(5, 7))

        # because we are working with the list of lists
        ticker = ticker[0]

        # check if ticker exists
        input_df = df_all.loc[df_all["Ticker"] == ticker].copy()
        print(f"len: {len(input_df)}, ticker: {ticker}")

        if len(input_df) < 50:
            print(f"{ticker} not enough data")
            continue

        df, BS, RZiS, CF = map_financial_data(
            df=df_all.loc[df_all["Ticker"] == ticker], db_conn=conn
        )

        if type(df) != str:
            try:
                df.drop(columns="level_0", inplace=True)
            except Exception:
                pass

            df.to_sql(ticker, schema="gpw_predictors", if_exists="replace", con=conn)
            print("uploaded df")
        else:
            print(f"ignoring {ticker} df")

        if type(BS) != str:
            try:
                BS.drop(columns="level_0", inplace=True)
            except Exception:
                pass
            BS.to_sql(ticker, schema="gpw_BS", if_exists="replace", con=conn)
            print("uploaded BS")
        else:
            print(f"ignoring {ticker} BS")

        if type(RZiS) != str:
            try:
                RZiS.drop(columns="level_0", inplace=True)
            except Exception:
                pass
            RZiS.to_sql(ticker, schema="gpw_RZiS", if_exists="replace", con=conn)
            print("uploaded RZiS")
        else:
            print(f"ignoring {ticker} RZiS")

        if type(CF) != str:
            try:
                CF.drop(columns="level_0", inplace=True)
            except Exception:
                pass
            CF.to_sql(ticker, schema="gpw_CF", if_exists="replace", con=conn)
            print("uploaded CF")
        else:
            print(f"ignoring {ticker} CF")
            continue

        print(f"processed {ticker}")
