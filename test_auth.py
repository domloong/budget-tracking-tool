import gspread

gc = gspread.service_account()

sh = gc.open("Budget Tracking Tool - 2022 - Tester")

print(sh.sheet1.get('A1'))