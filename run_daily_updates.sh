###################################################################################
# Script used to run daily updates of stock prices lists and tickers
###################################################################################

cd templates/python_scripts/ && python3 daily_upload.py && python3 daily_dropdowns_update.py 
