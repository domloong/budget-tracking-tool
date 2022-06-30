import gspread
import pandas as pd

gc = gspread.oauth()

sh = gc.open("Budget Tracking Tool - 2022")

result = sh.values_batch_get(["Mastercard Expense!B8:D", "VISA Expense!B8:D", "Income!B8:D"])

df = pd.DataFrame(result["valueRanges"][2]["values"])
