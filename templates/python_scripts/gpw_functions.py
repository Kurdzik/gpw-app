import datetime as d
import re
import time
from unittest import removeResult

import numpy as np
import pandas as pd
import requests
import unidecode
from bs4 import BeautifulSoup


def get_stock_prices(date_from, date_to, ticker="ALL", show_progress=True, wait=0.5):

    """
    Fetches data from GPW (Warsaw Stock Exchange)

    Using crawler to load data in batches: set date_from and date_to, the same
    Variables:

    date_from : type str, in a format dd-mm-yyyy
    date_to : type str, in a format dd-mm-yyyy
    ticker : type str, short name of a company of interest , default is 'all'
    show_progress : type bool, if set to True progress of scrapping is printed into the console
    wait = type float, the amount of time in seconds, between moving to the next page. Especially recommended while collecting lare amounts of data
    """

    date_from = date_from
    day_from = date_from[:2]
    month_from = date_from[3:5]
    year_from = date_from[-4:]

    date_to = date_to
    day_to = date_to[:2]
    month_to = date_to[3:5]
    year_to = date_to[-4:]
    ticker = ticker

    def get_day(x):
        if len(str(x.day)) < 2:
            return "0" + str(x.day)
        else:
            return str(x.day)

    def get_month(x):
        if len(str(x.month)) < 2:
            return "0" + str(x.month)
        else:
            return str(x.month)

    def get_year(x):
        return str(x.year)

    date_from = d.datetime(
        day=int(day_from), month=int(month_from), year=int(year_from)
    )

    date_to = d.datetime(day=int(day_to), month=int(month_to), year=int(year_to))

    all_values = pd.DataFrame()

    dates = [
        date_from + d.timedelta(days=x) for x in range((date_to - date_from).days + 1)
    ]

    for date in dates:

        if show_progress:
            print(
                "                                                                                                                                        ",
                end="\r",
            )
            print(
                f"scrapping pages... from {str(date_from)[:10]} to {str(date_to)[:10]}, selected tickers: {ticker}, progress: {round((dates.index(date)/len(dates))*100,2)}%",
                end="\r",
            )

        day = f"{get_day(date)}-{get_month(date)}-{get_year(date)}"

        time.sleep(wait)

        url = f"https://www.gpw.pl/archiwum-notowan?fetch=0&type=10&instrument=&date={day}&show_x=Poka??+wyniki"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html5lib")

        historical_values = {}
        l0, l1, l2, l3, l4, l5, l6, l7 = [], [], [], [], [], [], [], []

        for vals in soup.find_all("tr")[10:]:

            l0.append(vals.find_all("td")[0].text)
            l1.append(vals.find_all("td")[1].text)
            l2.append(vals.find_all("td")[2].text)
            l3.append(vals.find_all("td")[3].text)
            l4.append(vals.find_all("td")[4].text)
            l5.append(vals.find_all("td")[5].text)
            l6.append(vals.find_all("td")[7].text)
            l7.append(str(day))

        historical_values["Ticker"] = l0
        historical_values["Currency"] = l1
        historical_values["Open"] = l2
        historical_values["Max"] = l3
        historical_values["Min"] = l4
        historical_values["Close"] = l5
        historical_values["Volume_in_thousands"] = l6
        historical_values["Date"] = l7

        all_values = pd.concat([all_values, pd.DataFrame(historical_values)])

    if ticker != "ALL":
        if isinstance(ticker, list):
            all_values = all_values.loc[all_values["Ticker"].isin(ticker)]
        if isinstance(ticker, str):
            all_values = all_values.loc[all_values["Ticker"].str.contains(ticker)]

    for float_col in [
        col
        for col in all_values.columns.tolist()
        if col not in ["Date", "Currency", "Ticker"]
    ]:
        all_values[float_col] = all_values[float_col].astype(str).str.replace(",", ".")

    print(
        f"done, collected total of {len(all_values)} records                                                                                  ",
        end="\r",
    )
    all_values.reset_index(inplace=True)
    all_values.drop(columns="index", inplace=True)

    return all_values


def get_financial_data(comp):
    import numpy as np

    def get_vals(x, sep="r/r", sep2="k/k"):
        x = np.nan_to_num(x)

        try:
            data = re.split(sep, x)[0]
        except Exception:
            data = "0"

        if len(data) < 9:
            return data
        else:
            data = re.split(sep2, x)[0]
            return data

    def get_vals_v2(x, sep="~sektor", sep2="r/r"):
        x = np.nan_to_num(x)

        try:
            data = re.split(sep, x)[0]
        except Exception:
            data = "0"

        if len(data) < 9:
            return data

        else:
            data = re.split(sep2, x)[0]
            return data

    url_rzis = (
        f"https://www.biznesradar.pl/raporty-finansowe-rachunek-zyskow-i-strat/{comp}"
    )
    url_bs = f"https://www.biznesradar.pl/raporty-finansowe-bilans/{comp}"
    url_cf = f"https://www.biznesradar.pl/raporty-finansowe-przeplywy-pieniezne/{comp}"

    for x in range(5):
        try:
            RZiS = pd.read_html(url_rzis)[x].rename({"Unnamed: 0": "Index"}, axis=1)
            RZiS = RZiS[[col for col in RZiS.columns if "Unnamed" not in col]]

        except Exception:
            continue

    for x in range(5):
        try:
            BS = pd.read_html(url_bs)[x].rename({"Unnamed: 0": "Index"}, axis=1)
            BS = BS[[col for col in BS.columns if "Unnamed" not in col]]
        except Exception:
            continue

    for x in range(5):
        try:
            CF = pd.read_html(url_cf)[x].rename({"Unnamed: 0": "Index"}, axis=1)
            CF = CF[[col for col in CF.columns if "Unnamed" not in col]]
        except Exception:
            continue

    cols = [col[:4] for col in RZiS.columns.tolist()]

    for rep in [RZiS, BS, CF]:
        rep.columns = cols

    for col in cols:
        RZiS[col] = RZiS[col].apply(lambda x: get_vals_v2(x))
        RZiS[col] = RZiS[col].apply(lambda x: get_vals(x))
        BS[col] = BS[col].apply(lambda x: get_vals_v2(x))
        BS[col] = BS[col].apply(lambda x: get_vals(x))
        CF[col] = CF[col].apply(lambda x: get_vals_v2(x))
        CF[col] = CF[col].apply(lambda x: get_vals(x))

    url_market = f"https://www.biznesradar.pl/wskazniki-wartosci-rynkowej/{comp}"
    market_indicators = pd.read_html(url_market)[0].rename(
        {"Unnamed: 0": "Index"}, axis=1
    )
    market_indicators = market_indicators[
        [col for col in market_indicators.columns if "Unnamed" not in col]
    ]
    market_indicators.columns = [col[:7] for col in market_indicators.columns.tolist()]
    for col in market_indicators.columns.tolist():
        market_indicators[col] = market_indicators[col].apply(lambda x: get_vals_v2(x))
        market_indicators[col] = market_indicators[col].apply(
            lambda x: get_vals_v2(x, sep="k/k")
        )

    return BS, RZiS, CF, market_indicators


def map_financial_data(df, db_conn):
    """
    df : pd.DataFrame, in a form:
    Ticker	|   Currency |  Open        |   Max         |   Min         |	Close       |   Volume_in_thousands     |   Date

    db_conn : str, connection string of DB where table 'mapowanie' is located

    returns :
              df: for prediction model
              BS: for bashboards
              RZiS: for dashboards
              CF: for dashboards

    """

    def get_financial_data(comp):
        def get_vals(x, sep="r/r", sep2="k/k"):
            x = np.nan_to_num(x)

            try:
                data = re.split(sep, x)[0]
            except Exception:
                data = "0"

            if len(data) < 9:
                return data
            else:
                data = re.split(sep2, x)[0]
                return data

        def get_vals_v2(x, sep="~sektor", sep2="r/r"):
            x = np.nan_to_num(x)

            try:
                data = re.split(sep, x)[0]
            except Exception:
                data = "0"

            if len(data) < 9:
                return data

            else:
                data = re.split(sep2, x)[0]
                return data

        def check_conn(url, _timeout=5):
            """
            to check if we qre getting correct response
            """
            r = requests.get(url, timeout=_timeout).status_code
            retries = 0

            while True:

                if r != 200 and retries < 3:
                    time.sleep(2)
                    r = requests.get(url, timeout=_timeout).status_code
                    retries += 1
                    print(f"reconnecting..., retries {retries}")

                elif r != 200 and retries == 3:
                    print("unable to connect")
                    return "not connected"

                else:
                    print("connected!")
                    return "connected"

        url_rzis = f"https://www.biznesradar.pl/raporty-finansowe-rachunek-zyskow-i-strat/{comp}"
        url_bs = f"https://www.biznesradar.pl/raporty-finansowe-bilans/{comp}"
        url_cf = (
            f"https://www.biznesradar.pl/raporty-finansowe-przeplywy-pieniezne/{comp}"
        )
        print(f"links for {comp} collected")

        # ===================================================================================================================
        response = check_conn(url_rzis)
        if response == "connected":
            try:
                RZiS = pd.read_html(url_rzis)[2].rename({"Unnamed: 0": "Index"}, axis=1)
                RZiS = RZiS[[col for col in RZiS.columns if "Unnamed" not in col]]
                print(f"RZiS for {comp} collected")

            except Exception:
                try:
                    RZiS = pd.read_html(url_rzis)[1].rename(
                        {"Unnamed: 0": "Index"}, axis=1
                    )
                    RZiS = RZiS[[col for col in RZiS.columns if "Unnamed" not in col]]
                    print(f"RZiS for {comp} collected")
                except Exception:
                    RZiS = "not avaiable"
        elif response == "not connected":
            RZiS = "not avaiable"

        # ===================================================================================================================
        response = check_conn(url_bs)
        if response == "connected":
            try:
                BS = pd.read_html(url_bs)[2].rename({"Unnamed: 0": "Index"}, axis=1)
                BS = BS[[col for col in BS.columns if "Unnamed" not in col]]
                print(f"BS for {comp} collected")
            except Exception:
                try:
                    BS = pd.read_html(url_bs)[1].rename({"Unnamed: 0": "Index"}, axis=1)
                    BS = BS[[col for col in BS.columns if "Unnamed" not in col]]
                    print(f"BS for {comp} collected")
                except Exception:
                    BS = "not avaiable"

        elif response == "not connected":
            BS = "not avaiable"

        # ===================================================================================================================
        response = check_conn(url_cf)
        if response == "connected":
            try:
                CF = pd.read_html(url_cf)[1].rename({"Unnamed: 0": "Index"}, axis=1)
                CF = CF[[col for col in CF.columns if "Unnamed" not in col]]
                print(f"CF for {comp} collected")
            except Exception:
                try:
                    CF = pd.read_html(url_cf)[0].rename({"Unnamed: 0": "Index"}, axis=1)
                    CF = CF[[col for col in CF.columns if "Unnamed" not in col]]
                    print(f"CF for {comp} collected")
                except Exception:
                    CF = "not avaiable"
        elif response == "not connected":
            CF = "not avaiable"

        # ===================================================================================================================
        if type(BS) == str or type(RZiS) == str or type(CF) == str:
            market_indicators = "not avaiable"
            return BS, RZiS, CF, market_indicators

        else:
            cols = [col[:4] for col in RZiS.columns.tolist()]
            for rep in [RZiS, BS, CF]:
                rep.columns = cols

            for col in cols:
                RZiS[col] = RZiS[col].apply(lambda x: get_vals_v2(x))
                RZiS[col] = RZiS[col].apply(lambda x: get_vals(x))
                BS[col] = BS[col].apply(lambda x: get_vals_v2(x))
                BS[col] = BS[col].apply(lambda x: get_vals(x))
                CF[col] = CF[col].apply(lambda x: get_vals_v2(x))
                CF[col] = CF[col].apply(lambda x: get_vals(x))

            url_market = (
                f"https://www.biznesradar.pl/wskazniki-wartosci-rynkowej/{comp}"
            )
            market_indicators = pd.read_html(url_market)[0].rename(
                {"Unnamed: 0": "Index"}, axis=1
            )

            market_indicators = market_indicators[
                [col for col in market_indicators.columns if "Unnamed" not in col]
            ]
            market_indicators.columns = [
                col[:7] for col in market_indicators.columns.tolist()
            ]
            for col in market_indicators.columns.tolist():
                market_indicators[col] = market_indicators[col].apply(
                    lambda x: get_vals_v2(x)
                )
                market_indicators[col] = market_indicators[col].apply(
                    lambda x: get_vals_v2(x, sep="k/k")
                )

            return BS, RZiS, CF, market_indicators

    mapping_dict = dict(
        list(
            zip(
                pd.read_sql(
                    "select * from gpw.mapowanie", con=db_conn, index_col="index"
                )["gpw_name"],
                pd.read_sql(
                    "select * from gpw.mapowanie", con=db_conn, index_col="index"
                )["link"],
            )
        )
    )

    # check if company is present in our mapping dict

    try:
        mapping_dict[df["Ticker"].tolist()[0]]
        comp = mapping_dict[df["Ticker"].tolist()[0]]

    except Exception as e:
        print(e)

        return "not avaiable", "not avaiable", "not avaiable", "not avaiable"

    BS, RZiS, CF, market_indicators = get_financial_data(
        mapping_dict[df["Ticker"].tolist()[0]]
    )

    if type(BS) == str and type(RZiS) == str and type(CF) == str:
        return "not avaiable", "not avaiable", "not avaiable", "not avaiable"

    def quater(x):
        if x[3:5] in ["01", "02", "03"]:
            return "/Q1"
        elif x[3:5] in ["04", "05", "06"]:
            return "/Q2"
        elif x[3:5] in ["07", "08", "09"]:
            return "/Q3"
        else:
            return "Q4"

    def get_data(date, df, col_with_rownames="Index", row="Liczba akcji"):
        if date in df.columns.tolist():
            return df.loc[df[col_with_rownames] == row][date]
        else:
            date = df.columns.tolist()[-1]
            return df.loc[df[col_with_rownames] == row][date]

    def transform_to_float(x):
        if isinstance(x, str):
            x = x.replace(" ", "")
            x = x.replace(",", ".")

        try:
            return float(x)
        except Exception:
            return x

    if type(RZiS) != str:
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

    try:
        df["Year"] = df["Date"].str[-4:] + df["Date"].apply(lambda x: quater(x))
        df["Liczba akcji"] = df["Year"].apply(
            lambda x: get_data(x, df=market_indicators)
        )
        df["WK"] = df["Year"].apply(
            lambda x: get_data(x, df=market_indicators, row="Warto???? ksi??gowa na akcj??")
        )
        df["Aktywa obrotowe"] = df["Year"].apply(
            lambda x: get_data(
                x[:4], df=BS, col_with_rownames="Inde", row="Aktywa obrotowe"
            )
        )
        df["Zobowi??zania d??ugoterminowe"] = df["Year"].apply(
            lambda x: get_data(
                x[:4],
                df=BS,
                col_with_rownames="Inde",
                row="Zobowi??zania d??ugoterminowe",
            )
        )
        df["Zobowi??zania kr??tkoterminowe"] = df["Year"].apply(
            lambda x: get_data(
                x[:4],
                df=BS,
                col_with_rownames="Inde",
                row="Zobowi??zania kr??tkoterminowe",
            )
        )
        df["Przychody ze sprzeda??y na akcj??"] = df["Year"].apply(
            lambda x: get_data(
                x, df=market_indicators, row="Przychody ze sprzeda??y na akcj??"
            )
        )
        df["Zysk na akcj??"] = df["Year"].apply(
            lambda x: get_data(x, df=market_indicators, row="Zysk na akcj??")
        )
        df["Zysk operacyjny na akcj??"] = df["Year"].apply(
            lambda x: get_data(x, df=market_indicators, row="Zysk operacyjny na akcj??")
        )
        df["Enterprise Value na akcj??"] = df["Year"].apply(
            lambda x: get_data(x, df=market_indicators, row="Enterprise Value na akcj??")
        )
        df["EV / P"] = df["Year"].apply(
            lambda x: get_data(
                x, df=market_indicators, row="EV / Przychody ze sprzeda??y"
            )
        )
        df["EV / EBIT"] = df["Year"].apply(
            lambda x: get_data(x, df=market_indicators, row="EV / EBIT")
        )
        df["EV / EBITDA"] = df["Year"].apply(
            lambda x: get_data(x, df=market_indicators, row="EV / EBITDA")
        )

        for col in [
            float_col
            for float_col in df.columns.tolist()
            if float_col not in ["Date", "Ticker", "Currency", "Year"]
        ]:
            df[col] = df[col].apply(lambda x: transform_to_float(x))

        df["C/ZO"] = df["Close"] / df["Zysk operacyjny na akcj??"]
        df["C/WK"] = df["Close"] / df["WK"]
        df["Cena / WK Grahama"] = df["Close"] / (
            df["Zobowi??zania d??ugoterminowe"] + df["Zobowi??zania kr??tkoterminowe"]
        )
        df["C/P"] = df["Close"] / df["Przychody ze sprzeda??y na akcj??"]
        df["C/Z"] = df["Close"] / df["Zysk na akcj??"]
        df["Close_pct"] = df["Close"].pct_change().mul(100)
        df["Open_pct"] = df["Open"].pct_change().mul(100)
        df["Max_pct"] = df["Max"].pct_change().mul(100)
        df["Min_pct"] = df["Min"].pct_change().mul(100)

        print(f"df for {comp} collected")

    except Exception:
        df = "not avaiable"

    return df, BS, RZiS, CF


def train_test_split(
    X,
    Y=None,
    split_by_date=False,
    split_by_proportion=0.8,
    return_shape="3D",
    return_type=None,
):
    """
    Splits dataset pandas DataFrame into train and test sets

    Variables:
    :df - Data Frame which will be splitted
    :X - Array/Dataframe containing X values
    :Y - Array/Series containing Y values
    :split_by_date - str 'YYYY-MM-DD', everything before it will be train set, and after it, test set
    :train_size - size of a train_set
    :return_shape - 2D or 3D, determines what vector shape will be returned

    :return 'X_train','X_test','y_train','y_test'

    """
    if split_by_date:
        split_size = split_by_date

    else:
        split_size = int(len(X) * split_by_proportion)

    if Y != None:
        X_train, Y_train = X[:split_size], Y[:split_size]
        X_test, Y_test = X[split_size:], Y[split_size:]

        if return_type == "numpy":
            X_train = np.array(X_train).astype(np.float16)
            X_test = np.array(X_test).astype(np.float16)
            X_train = np.array(X_train).astype(np.float16)
            X_test = np.array(X_test).astype(np.float16)
            Y_train = np.array(Y_train).astype(np.float16)
            Y_test = np.array(Y_test).astype(np.float16)

        print(
            "X_train shape:",
            X_train.shape,
            "X_test shape:",
            X_test.shape,
            "y_train shape:",
            Y_train.shape,
            "y_test shape:",
            Y_test.shape,
        )

        if return_shape == "2D":
            return X_train, X_test, Y_train, Y_test
        if return_shape == "3D":
            return (
                np.expand_dims(X_train, -1),
                np.expand_dims(X_test, -1),
                np.expand_dims(Y_train, -1),
                np.expand_dims(Y_test, -1),
            )

    else:
        X_train = X[:split_size]
        X_test = X[split_size:]

        if return_type == "numpy":
            X_train = np.array(X_train).astype(np.float16)
            X_test = np.array(X_test).astype(np.float16)

        print("X_train shape:", X_train.shape, "X_test shape:", X_test.shape)

        if return_shape == "2D":
            return X_train, X_test
        if return_shape == "3D":
            return np.expand_dims(X_train, -1), np.expand_dims(X_test, -1)
