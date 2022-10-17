from datetime import datetime

import gspread
import numpy as np
import pandas as pd

import config

pd.set_option("display.max_rows", None, "display.max_columns", None)


def extract_gsheet_into_dataframes(sheet_values):
    dict_df = {}

    for tab, value_ranges in zip(config.sheet_tabs.keys(), sheet_values["valueRanges"]):
        df = pd.DataFrame(value_ranges["values"])
        df = df.drop(df[df[0] == ""].index)
        df = df.rename(columns={0: "Date", 1: "Description", 2: "Amount"})
        df.Date = df.Date.apply(lambda x: datetime.strptime(x, config.date_formats["sheet"]))
        df.Amount = df.Amount.apply(lambda x: float(x.replace("$", "").replace(",", "")))
        dict_df[tab] = df

    return dict_df


def extract_mastercard_into_dataframes(df_sheet):
    df = pd.read_csv("report.csv")
    df = df[["Date", "Description", "Amount"]]
    df["Date"] = df["Date"].apply(lambda x: datetime.strptime(x, config.date_formats["mastercard"]))
    df = df[df.Date > df_sheet.Date.max()]

    df_expenses = df[df.Amount < 0]
    df_expenses.Amount = df_expenses.Amount.apply(abs)

    df_refunds = df[(df.Amount > 0) & (~df.Description.str.contains("Payment"))]

    return df_expenses, df_refunds


def format_cibc_csv(df):
    df.loc[-1] = df.columns.values
    df.sort_index(inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.columns = range(df.columns.size)
    df.loc[0, 3] = np.NaN
    df = df.rename(columns={0: "Date", 1: "Description", 2: "Expenses", 3: "Refunds"})
    df.Date = df.Date.apply(lambda x: datetime.strptime(x, config.date_formats["cibc"]))

    return df


def extract_visa_into_dataframes(df_sheet):
    df = pd.read_csv("cibc.csv")
    df = format_cibc_csv(df)

    df_expense = df[["Date", "Description", "Expenses"]].dropna()
    df_expense = df_expense.rename(columns={"Expenses": "Amount"})

    df_refund = df[["Date", "Description", "Refunds"]].dropna()
    df_refund = df_refund.rename(columns={"Refunds": "Amount"})
    df_refund = df_refund[~df_refund.Description.str.contains("PAYMENT")]

    return df_expense, df_refund


if __name__ == "__main__":
    sh = gspread.service_account().open(config.SHEET_NAME)
    sheet_values = sh.values_batch_get([tab_name + "!" + config.SHEET_RANGE for tab_name in config.sheet_tabs.values()])

    dict_df = extract_gsheet_into_dataframes(sheet_values)

    df_mastercard_expense, df_mastercard_refund = extract_mastercard_into_dataframes(dict_df["mastercard"])

    df_visa_expense, df_visa_refund = extract_visa_into_dataframes(dict_df["visa"])


# df_new = pd.concat([df_new_expenses, df_sheet])

# df_new["Date"] = df_new["Date"].apply(lambda x: datetime.strftime(x, "%m-%d-%Y"))

# df_new = df_new.sort_values("Date")

# ws = sh.worksheet("Mastercard Expense")

# values = df_new.values.tolist()

# ws.update("B8:D", values)
