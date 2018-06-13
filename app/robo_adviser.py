from dotenv import load_dotenv
import json
import os
import csv
import datetime
import requests
from IPython import embed

load_dotenv()

#adapted from source: https://github.com/prof-rossetti/stocks-app-py

def parse_response(response_text):
    if isinstance(response_text, str):
        response_text = json.loads(response_text)

    results = []
    time_series_daily = response_text["Time Series (Daily)"]
    for trading_date in time_series_daily:
        prices = time_series_daily[trading_date]
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename="data\prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "1. open", "2. high", "3. low", "4. close", "5. volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"], # change attribute name to match project requirements
                "1. open": d["open"],
                "2. high": d["high"],
                "3. low": d["low"],
                "4. close": d["close"],
                "5. volume": d["volume"]
            }
            writer.writerow(row)

def is_valid_ticker(symbol):
    try:
        float(symbol)
        return True
    except Exception as e:
        return False

def wrong_ticker_format():
    print("That format is not valid for a ticker, please enter the correct ticker symbol in capital letters")
    return

api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."

symbol = input("Please enter the ticker you would like to see: ")

request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + symbol + "&apikey=" + api_key
response = requests.get(request_url)

if "Error Message" in response.text:
    print("Invalid ticker, please enter the ticker of a listed entity.")
    quit("Please try again.")

response_body = json.loads(response.text)

metadata = response_body["Meta Data"]
data = response_body["Time Series (Daily)"]
dates = list(data)
latest_daily_data = data[dates[1]]
size = len(data)
if size > 100:
    size = 100
latest_hundred_days_data = []
for i in range(size):
    latest_hundred_days_data.append(data[dates[i]])

high_price = []
for row in latest_hundred_days_data:
    high_price.append(row["2. high"])

low_price = []
for row in latest_hundred_days_data:
    low_price.append(row["3. low"])

#> {'1. open': '353.8000',
#> '2. high': '355.5300',
#> '3. low': '350.2100',
#> '4. close': '351.6000',
#> '5. volume': '6921687'}
latest_price = latest_daily_data["4. close"]
latest_price = float(latest_price)
latest_price_usd = "${0:,.2f}".format(latest_price)

highest_price = max(high_price)
highest_price = float(highest_price)
highest_price_usd = "${0:,.2f}".format(highest_price)

lowest_price= min(low_price)
lowest_price = float(lowest_price)
lowest_price_usd = "${0:,.2f}".format(lowest_price)

if int(latest_price) <= int(1.1 * lowest_price) and int(latest_price) >= int(lowest_price):
    recommendation = "Buy"
elif int(latest_price) <= int(highest_price) and int(latest_price) >= int(0.9 * highest_price):
    recommendation = "Sell"
else:
    recommendation = "Hold"

if recommendation == "Buy":
    explanation = "The most recent closing price is within 10% of the recent average low price and will likely return to the middle of its range."
elif recommendation == "Sell":
    explanation = "The most recent closing price is within 10% of the recent average high price and will likely return to the middle of its range."
else:
    recommendation == "Hold"
    explanation = "The stock is fairly valued based on the price relative to the recent average high and low prices."


print("SUMMARY")
print("-------------------------------------------------")
print("Ticker: " + symbol)
print("Last refreshed on " + max(dates))
print(f"Latest daily closing price for {symbol} is: {latest_price_usd}")
print(f"The recent average high price over the last 100 trading days was {highest_price_usd}")
print(f"The recent average low price over the last 100 trading days was {lowest_price_usd}")
print(f"Recommended action for this stock is to {recommendation}")
print(f"{explanation}")

daily_prices = parse_response(response.text)
write_prices_to_file(prices=daily_prices, filename="data\prices.csv")
