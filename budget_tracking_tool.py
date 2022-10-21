from datetime import datetime
from pathlib import Path

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


def extract_mastercard_into_dataframes(df_sheet, df):
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


def split_cibc_df(df):
    df_expense = df[["Date", "Description", "Expenses"]].dropna()
    df_expense = df_expense.rename(columns={"Expenses": "Amount"})

    df_revenue = df[["Date", "Description", "Refunds"]].dropna()
    df_revenue = df_revenue.rename(columns={"Refunds": "Amount"})

    return df_expense, df_revenue


def extract_visa_into_dataframes(df_sheet, df):
    df = df[df.Date > df_sheet.Date.max()]

    df_expense, df_revenue = split_cibc_df(df)

    df_revenue = df_revenue[~df_revenue.Description.str.contains("PAYMENT")]

    return df_expense, df_revenue


def extract_chequing_into_dataframes(df_sheet, df):
    df = df[df.Date > df_sheet.Date.max()]

    df_expense, df_revenue = split_cibc_df(df)

    df_expense = df_expense[~df_expense.Description.str.contains("INTERNET TRANSFER|MASTERCARD", regex=True)]

    df_revenue = df_revenue[~df_revenue.Description.str.contains("INTERNET TRANSFER")]

    return df_expense, df_revenue


def extract_from_csvs(dict_df):
    dict_expenses = {}
    dict_revenues = {}
    csv_path = Path(config.csv_path)

    for csv in config.csv_list:
        df = pd.read_csv(csv_path / csv)
        if csv == "report.csv":
            dict_expenses["mastercard"], dict_revenues["mastercard"] = extract_mastercard_into_dataframes(
                dict_df["mastercard"], df
            )
        else:
            df = format_cibc_csv(df)
            if df.Description.str.contains("2nd Site|INTERNET TRANSFER", regex=True).any():
                dict_expenses["chequing"], dict_revenues["chequing"] = extract_chequing_into_dataframes(
                    dict_df["chequing"], df
                )
            else:
                dict_expenses["visa"], dict_revenues["visa"] = extract_visa_into_dataframes(dict_df["visa"], df)

    return dict_expenses, dict_revenues


def upload_to_sheet(tab_name, df):
    ws = sh.worksheet(tab_name)
    values = df.values.tolist()
    ws.update(config.SHEET_RANGE, values, value_input_option="USER_ENTERED")


def construct_upload_df(current_df, new_df):
    df = pd.concat([current_df, new_df])
    df = df.sort_values("Date")
    df["Date"] = df["Date"].apply(lambda x: datetime.strftime(x, config.date_formats["sheet"]))
    df["Amount"] = df["Amount"].astype(float)

    return df


def batch_upload_to_sheet(sheet, expenses, revenues):
    new_data = expenses

    new_data["expense"] = pd.concat([expense for expense in expenses.values()])
    new_data["income"] = pd.concat([revenue for revenue in revenues.values()])

    for key, value in config.sheet_tabs.items():
        new_df = construct_upload_df(sheet[key], new_data[key])
        upload_to_sheet(value, new_df)


if __name__ == "__main__":
    sh = gspread.service_account().open(config.SHEET_NAME)

    sheet_tabs = [tab_name + "!" + config.SHEET_RANGE for tab_name in config.sheet_tabs.values()]
    sheet_values = sh.values_batch_get(sheet_tabs)

    dict_sheet_df = extract_gsheet_into_dataframes(sheet_values)

    dict_updated_expenses, dict_updated_revenues = extract_from_csvs(dict_sheet_df)

    batch_upload_to_sheet(dict_sheet_df, dict_updated_expenses, dict_updated_revenues)
