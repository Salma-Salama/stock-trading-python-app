# US Stock Data API Fetcher

A Python script that fetches US stock market data from an external API, handles paginated API responses, and saves the collected data into a CSV file.

## Features

* Fetches US stock data from an API
* Handles paginated API responses
* Combines results from multiple API pages
* Stores the collected data in memory
* Exports the final dataset to a CSV file
* Supports API authentication using an API key

## Requirements

* You will find all required packages in requirements.txt

Install the required package using:

```bash
pip install -r requirements.txt
```

## Configuration

The script requires an API key.

It is recommended to store the API key in an environment variable instead of writing it directly inside the Python code.

Example:

```bash
export POLYGON_API_KEY="your_api_key"
```

## Usage

Run the script from the terminal:

```bash
python script.py
```

The script will:

1. Send a request to the stock market API.
2. Retrieve the stock data from the response.
3. Follow the API's pagination links when more results are available.
4. Combine all results into one collection.
5. Save the collected data into a CSV file.

## Output

The collected stock data is saved as:

```text
stocks.csv
```

## License

This project is intended for learning and educational purposes.
