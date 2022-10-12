import gspread
import pandas as pd

from datetime import datetime

gc = gspread.service_account()

sh = gc.open("Budget Tracking Tool - 2022 - Tester")

result = sh.values_batch_get(["Mastercard Expense!B8:D", "VISA Expense!B8:D", "Income!B8:D"])

df_sheet = pd.DataFrame(result["valueRanges"][0]["values"])
df_sheet = df_sheet.drop(df_sheet[df_sheet[0] == ""].index)
df_sheet[0] = df_sheet[0].apply(lambda x: datetime.strptime(x, "%m-%d-%Y"))
df_sheet = df_sheet.rename(columns = {0:"Date", 1:"Description", 2:"Amount"})

df = pd.read_csv("report.csv")
df = df[["Date", "Description", "Amount"]]

df["Date"] = df["Date"].apply(lambda x: datetime.strptime(x, "%m/%d/%Y"))

df_new_expenses = df[df.Amount < 0 ]

df_new = pd.concat([df_new_expenses, df_sheet])

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


# if __name__ == "__main__":
#     main()