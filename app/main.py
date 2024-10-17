import pandas as pd
import yfinance as yf
import numpy as np
import time as time
from datetime import datetime

# Getting todays date and 10 years ago date
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
    
# Function to get the candlestick data and financial data
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
    
    
# Main function
if __name__ == "__main__":
    get_stat_data(trackers)
    get_candlestick_data(trackers)
