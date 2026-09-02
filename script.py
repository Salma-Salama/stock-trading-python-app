from dotenv import load_dotenv
import os
import requests
import time
import csv

load_dotenv()

polygon_api_key = os.getenv("polygon_api_key")
limit = 1000

url = f'https://api.massive.com/v3/reference/tickers?market=stocks&active=true&order=asc&limit={limit}&sort=ticker&apiKey={polygon_api_key}'

def fetch_stock_data(url):
    full_data = []
    while url:
        # Reading the data from the API
        response = requests.get(url)
        # store it
        data = response.json()

        # Check if the response contains the expected data or if it returns an error message
        if "results" not in data:
            if "maximum requests per minute" in data.get("error", ""):
                print("Rate limit reached. Waiting...")
                time.sleep(60)
                continue

            print("Unexpected error:", data)
            break

        # Adding the  fetched data to the full_data list
        full_data.extend(data['results'])

        # getting next url
        url = data.get("next_url")
        # Making sure to add the API key to the next_url if it exists (this is important for pagination)
        if url:
            url = f"{url}&apiKey={polygon_api_key}"

    return full_data


if __name__ == "__main__":
    full_data = fetch_stock_data(url)

    with open("stocks.csv", "w", newline="", encoding="utf-8") as file:
        fieldnames = full_data[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(full_data)
 



