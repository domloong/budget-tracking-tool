SHEET_NAME = "Budget Tracking Tool - 2022"
SHEET_RANGE = "B8:D"
COLUMN_NAMES = ["Date", "Description", "Amount"]

sheet_tabs = {
    "mastercard": "Mastercard Expense",
    "visa": "VISA Expense",
    "chequing": "Chequing Expense",
    "income": "Income",
    "expense": "Expenses",
}

date_formats = {"sheet": "%m-%d-%Y", "mastercard": "%m/%d/%Y", "cibc": "%Y-%m-%d"}

csv_list = ["report.csv", "cibc.csv", "cibc-2.csv"]

csv_path = "/Users/dom.loong/Downloads/"
