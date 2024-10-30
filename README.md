# Streamlit Stock Dashboard
 
A Streamlit application that uses the yFinance API to gather data and visualize stock market data, including price, volume, and moving averages. The app also includes a sidebar for user input to select the stock symbol, date range, and moving average period.

[Try it out here!](https://app-stock-dashboard-rcf3kwydlx5knj9njeumpz.streamlit.app)

## Data Scraping and Preparation

The application begins by scraping the list of S&P 500 companies from Wikipedia. This is done using the `pandas` library to read the HTML table from the Wikipedia page and save it as a CSV file. The list of stock symbols is then extracted and prepared for further data retrieval.

```python
import pandas as pd
import yfinance as yf
import numpy as np
import time as time
from datetime import datetime

# Getting today's date and date from 5 years ago
now = datetime.today().strftime('%Y-%m-%d')
fiveyrsago = datetime.today() - pd.DateOffset(years=5)
fiveyrsago = fiveyrsago.strftime('%Y-%m-%d')

# Get the stock symbols from Wikipedia S&P 500 List
sp500link = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies#S&P_500_component_stocks"
tickers = pd.read_html(sp500link, header=0)[0]
tickers.to_csv("Streamlit-Stock-Dashboard/tickers_list.csv", index=False)
# Making the Symbol column into a list to later iterate through.
trackers = tickers['Symbol'].tolist()
print("S&P500 data scraped.")
```
### Explanation

#### Importing Libraries:
- Imports necessary libraries for data manipulation (`pandas`), financial data retrieval (`yfinance`), numerical operations (`numpy`), and date/time handling (`datetime`).

#### Getting Today's Date and Date from 5 Years Ago:
- `now` stores today's date in the format `YYYY-MM-DD`.
- `fiveyrsago` stores the date from 5 years ago in the same format.

#### Scraping S&P 500 Stock Symbols from Wikipedia:
- `sp500link` stores the URL of the Wikipedia page containing the list of S&P 500 companies.
- `tickers` uses `pandas` to read the HTML table from the Wikipedia page and stores it as a DataFrame.
- The DataFrame is then saved to a CSV file named `tickers_list.csv` in the `Streamlit-Stock-Dashboard` directory.

#### Preparing the List of Stock Symbols:
- Extracts the `Symbol` column from the DataFrame and converts it into a list named `trackers`.
- Prints a message indicating that the S&P 500 data has been successfully scraped.

This code ensures that the application has the most up-to-date list of S&P 500 companies, which is essential for retrieving accurate financial data.

## yFinance API Functions

### Function: `get_stat_data`

The `get_stat_data` function retrieves valuation data for a list of stock symbols using the yFinance API and saves the data to a CSV file.

#### Parameters:
- `trackers` (list): A list of stock symbols to retrieve data for.

#### Process:
1. Initializes an empty list `valuations` to store the valuation data.
2. Iterates over each stock symbol in the `trackers` list:
   - Replaces any periods in the symbol with hyphens to match yFinance's format.
   - Uses the yFinance `Ticker` object to retrieve the stock's valuation data.
   - Adds the stock symbol to the valuation data.
   - Appends the valuation data to the `valuations` list.
   - Prints a success message if the data is downloaded successfully.
   - Prints an error message if the data download fails.
3. Concatenates the `valuations` list into a DataFrame.
4. Saves the DataFrame to a CSV file named `valuations_data.csv` in the `Streamlit-Stock-Dashboard` directory.
5. Prints a message indicating that the valuations data has been saved to the CSV file.

#### Code:
```python
def get_stat_data(trackers):
    valuations = []
    
    for tracker in trackers:
        try:
            tracker = tracker.replace(".", "-")
            ticker = yf.Ticker(tracker)
            valuation = ticker.info
            valuation['Symbol'] = tracker
            valuations.append(valuation)
            print(f"{tracker} data downloaded.")
            
        except Exception as e:
            print(f"{tracker} data FAILED to download.")
            print(e)
    
    # Concatenate valuations data into a DataFrame
    final_valuations = pd.DataFrame(valuations)
    final_valuations.to_csv("Streamlit-Stock-Dashboard/valuations_data.csv", index=False)
    print("Valuations data saved to CSV.")
```
### Function: `get_candlestick_data`

The `get_candlestick_data` function retrieves historical candlestick data for a list of stock symbols using the yFinance API and saves the data to a CSV file.

#### Parameters:
- `trackers` (list): A list of stock symbols to retrieve data for.
- `period` (str): The period over which to retrieve the data (e.g., '1mo', '3mo', '1y').
- `interval` (str): The interval at which to retrieve the data (e.g., '1d', '1wk', '1mo').

#### Process:
1. Initializes an empty list `candlestick_data` to store the historical data.
2. Iterates over each stock symbol in the `trackers` list:
   - Replaces any periods in the symbol with hyphens to match yFinance's format.
   - Uses the yFinance `Ticker` object to retrieve the stock's historical data for the specified period and interval.
   - Adds the stock symbol to the historical data.
   - Appends the historical data to the `candlestick_data` list.
   - Prints a success message if the data is downloaded successfully.
   - Prints an error message if the data download fails.
3. Concatenates the `candlestick_data` list into a DataFrame.
4. Saves the DataFrame to a CSV file named `candlestick_data.csv` in the `Streamlit-Stock-Dashboard` directory.
5. Prints a message indicating that the candlestick data has been saved to the CSV file.

#### Example Usage:
```python
def get_candlestick_data(trackers):
    candle_data = []
    financial_data = []
    
    for tracker in trackers:
        try:
            tracker = tracker.replace(".", "-")
            data = yf.download(tracker, start=fiveyrsago, end=now)
            data['Symbol'] = tracker
            candle_data.append(data)
            print(f"{tracker} candlestick data downloaded.")
            
            # Download financial data
            ticker = yf.Ticker(tracker)
            financials = ticker.financials.T
            financials['Symbol'] = tracker
            financial_data.append(financials)
            print(f"{tracker} financial data downloaded.")
            
        except Exception as e:
            print(f"{tracker} data FAILED to download.")
            print(e)
            
    # Concatenate candlestick data into a csv file
    final_candle_data = pd.concat(candle_data)
    final_candle_data.to_csv("Streamlit-Stock-Dashboard/candle_data.csv")
    print("Candlestick data saved to CSV.")
    
    # Concatenate financial data into a csv file
    final_financial_data = pd.concat(financial_data)
    final_financial_data.to_csv("Streamlit-Stock-Dashboard/financial_data.csv")
    print("Financial data saved to CSV.")
```
## Streamlit Application


