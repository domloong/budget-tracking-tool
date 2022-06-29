import gspread

gc = gspread.oauth()

gc.create('Example spreadsheet')

sh = gc.open("Example spreadsheet")

print(sh.sheet1.get('A1'))