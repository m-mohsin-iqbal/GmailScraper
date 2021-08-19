# import pygsheets
# import pandas as pd
# #authorization
# gc = pygsheets.authorize(client_secret='client.json')
# new_row = ['firstname', 'lastname', 'Email']
# worksheet = gc.open('PY').sheet1
# cells = worksheet.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
# last_row = len(cells)
# print(last_row)
# worksheet = worksheet.insert_rows(last_row, number=1, values= new_row)
# # Create empty dataframe
# df = pd.DataFrame()
# # Create a column
# df['name'] = ['John']
# df['email'] = 'test@gmail.com'
# df['password'] = 'pass123'

# # #open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
# sh = gc.open('PY')
#
# # select the first sheet
# wks = sh[0]
#
# # update the first sheet with df, starting at cell B2.
# wks.insert_rows(wks.rows, values=['John'], inherit=True)
import gspread

gc = gspread.service_account(filename='creds.json')

# Open a sheet from a spreadsheet in one go
wks = gc.open("PY").sheet1
values = ["Mohsin",'test@gmail.com','pass1234']
wks.append_row(values)
