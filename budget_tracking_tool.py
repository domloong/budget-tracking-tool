from os import set_inheritable
import gspread
import pandas as pd


def main():
    import_csv()
        figure out which csv belongs to which tabs

            split between expenses and income

        return all imports as a dictionary containing the data


    update_expenses()

        get all values from each sheet 

        compare timestamp and the csv data where not in sheet  

        combine to make a new dataframe


    update_income()

    similar as above but for expenses


    Also need to ensure we deal with dollar amount as string and upload back as float


if __name__ == "__main__":
    main()