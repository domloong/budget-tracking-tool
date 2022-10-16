from datetime import datetime

import gspread
import pandas as pd

import config


def extract_gsheet_into_dataframes(sheet_values):
    dict_df = {}

    for tab, value_ranges in zip(config.sheet_tabs.keys(), sheet_values["valueRanges"]):
        df = pd.DataFrame(value_ranges["values"])
        df = df.drop(df[df[0] == ""].index)
        df = df.rename(columns = {0:"Date", 1:"Description", 2:"Amount"})
        df.Date = df.Date.apply(lambda x: datetime.strptime(x, config.date_formats["sheet"]))
        df.Amount = df.Amount.apply(lambda x: float(x.replace("$", "").replace(",", "")))
        dict_df[tab] = df

    return dict_df


if __name__ == "__main__":
    sh = gspread.service_account().open(config.SHEET_NAME)
    sheet_values = sh.values_batch_get([tab_name + "!" + config.SHEET_RANGE for tab_name in config.sheet_tabs.values()])

    dict_df = extract_gsheet_into_dataframes(sheet_values)



# df = pd.read_csv("report.csv")
# df = df[["Date", "Description", "Amount"]]

# df["Date"] = df["Date"].apply(lambda x: datetime.strptime(x, "%m/%d/%Y"))

# df_new_expenses = df[(df.Amount < 0) & (df.Date > df_sheet.Date.max())]
# df_new_expenses.Amount = df_new_expenses.Amount.apply(abs)

# df_new = pd.concat([df_new_expenses, df_sheet])

# df_new["Date"] = df_new["Date"].apply(lambda x: datetime.strftime(x, "%m-%d-%Y"))

# df_new = df_new.sort_values("Date")

# ws = sh.worksheet("Mastercard Expense")

# values = df_new.values.tolist()

# df_refunds = df[(df.Amount > 0) & (~df.Description.str.contains("Payment"))]

# ws.update("B8:D", values)

# def main():
#     import_csv()
#         figure out which csv belongs to which tabs

#             split between expenses and income

#         return all imports as a dictionary containing the data


#     update_expenses()

#         get all values from each sheet 

#         compare timestamp and the csv data where not in sheet  

#         combine to make a new dataframe


#     update_income()

#     similar as above but for expenses


#     Also need to ensure we deal with dollar amount as string and upload back as float


#     Also think about how to handle yearly change


