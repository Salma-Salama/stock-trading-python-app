from dotenv import load_dotenv
import os
import requests
import time 
from datetime import datetime
from zoneinfo import ZoneInfo
import snowflake.connector

load_dotenv()


def connect_to_snowflake():
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    return conn




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


def add_ingestedat_column(full_data, pipeline_start_time):
    for row in full_data:
        row['ingested_at'] = pipeline_start_time
    return full_data

def insert_data_into_snowflake(full_data):
    conn = None
    cursor = None

    try:
        conn = connect_to_snowflake()
        cursor = conn.cursor()

        # Prepare the insert statement
        insert_query = """
            INSERT INTO stock_tickers (ticker, 
                                        name, 
                                        market,
                                        locale ,
                                        primary_exchange ,
                                        type ,
                                        active ,
                                        currency_name ,
                                        cik ,
                                        composite_figi ,
                                        share_class_figi ,
                                        last_updated_utc,
                                        ingested_at
                                        )  
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # covert the dictionary to tuples for insertion
        rows_tuple = []
        for row in full_data:
            rows_tuple.append  ((
                row.get('ticker'),
                row.get('name'),
                row.get('market'),
                row.get('locale'),
                row.get('primary_exchange'),
                row.get('type'),
                row.get('active'),
                row.get('currency_name'),
                row.get('cik'),
                row.get('composite_figi'),
                row.get('share_class_figi'),
                row.get('last_updated_utc'),
                row.get('ingested_at')
            ))

        # Execute the insert statement for each row in full_data
        cursor.executemany(insert_query, rows_tuple)

        # Commit the transaction
        conn.commit()

        print(f"{len(rows_tuple)} rows successfully loaded into Snowflake.")

    except Exception as e:
        print("Error loading data into Snowflake:", e)

        # Undo the transaction if something failed
        if conn:
            conn.rollback()

        raise

    finally:
        # close the cursor and connection
        if cursor:
            cursor.close()

        if conn:
            conn.close()    


if __name__ == "__main__":

    print("Starting API - Snowflake pipeline...")

    pipeline_start_time = datetime.now(ZoneInfo("Africa/Cairo"))

    full_data = fetch_stock_data(url)
    print(
        f"API extraction finished. "
        f"Total rows: {len(full_data)}"
    )
    if full_data:
        full_data = add_ingestedat_column(full_data, pipeline_start_time)
        print(
               "Ingestion timestamp:",
               full_data[0]["ingested_at"]
            )
        insert_data_into_snowflake(full_data)

    else:
        print("No data returned. Nothing loaded.")

    print("Pipeline finished.")        


