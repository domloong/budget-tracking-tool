import config
import gspread
import pandas as pd

from datetime import datetime

gc = gspread.service_account()

sh = gc.open(config.SHEET_NAME)

result = sh.values_batch_get(["Mastercard Expense!B8:D", "VISA Expense!B8:D", "Income!B8:D"])

df_sheet = pd.DataFrame(result["valueRanges"][0]["values"])
df_sheet = df_sheet.drop(df_sheet[df_sheet[0] == ""].index)
df_sheet[0] = df_sheet[0].apply(lambda x: datetime.strptime(x, "%m-%d-%Y"))
df_sheet = df_sheet.rename(columns = {0:"Date", 1:"Description", 2:"Amount"})
df_sheet.Amount = df_sheet.Amount.apply(lambda x: float(x[1:]))

df = pd.read_csv("report.csv")
df = df[["Date", "Description", "Amount"]]

df["Date"] = df["Date"].apply(lambda x: datetime.strptime(x, "%m/%d/%Y"))

df_new_expenses = df[(df.Amount < 0) & (df.Date > df_sheet.Date.max())]
df_new_expenses.Amount = df_new_expenses.Amount.apply(abs)

df_new = pd.concat([df_new_expenses, df_sheet])

df_new["Date"] = df_new["Date"].apply(lambda x: datetime.strftime(x, "%m-%d-%Y"))

df_new = df_new.sort_values("Date")

ws = sh.worksheet("Mastercard Expense")

values = df_new.values.tolist()

df_refunds = df[(df.Amount > 0) & (~df.Description.str.contains("Payment"))]

ws.update("B8:D", values)

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