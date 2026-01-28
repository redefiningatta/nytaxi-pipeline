#!/usr/bin/env python
# coding: utf-8

# import os
# import argparse
# import pandas as pd
# from sqlalchemy import create_engine
# from tqdm.auto import tqdm

# def load_nytaxi_data(params):
#     user = params.user
#     password = params.password
#     host = params.host
#     port = params.port
#     db = params.db
#     table_name = params.table_name
    
#     month = str(params.month).zfill(2)

#     url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{params.colour}/{params.colour}_tripdata_{params.year}-{month}.csv.gz"
#     engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

#     print(f"Loading data from {url} into table {table_name}")
    
#     df_iter = pd.read_csv(
#             url,
#             iterator=True,
#             chunksize=100000,
#             low_memory=False
#         )

#     for df_chunk in tqdm(df_iter):
#         t_cols = [col for col in df_chunk.columns if 'tpep' in col or 'pickup' in col or 'dropoff' in col]
#         for col in t_cols:
#             df_chunk[col] = pd.to_datetime(df_chunk[col])
        
#         # Insert chunk
#         df_chunk.to_sql(
#             name=table_name,
#             con=engine,
#             if_exists="append",
#             index=False
#         )
#         print("Inserted chunk")

# if __name__ == "__main__":
    
#     parser = argparse.ArgumentParser(description="Load NY Taxi data into Postgres")
#     parser.add_argument("--user", required=True, help="Postgres username")
#     parser.add_argument("--password", required=True, help="Postgres password")
#     parser.add_argument("--host", required=True, help="Postgres host")
#     parser.add_argument("--port", required=True, help="Postgres port")
#     parser.add_argument("--db", required=True, help="Postgres database name")
#     parser.add_argument("--table_name", required=True, help="Target table name in Postgres")
#     parser.add_argument("--colour", required=True, default=os.getenv("COLOUR", "yellow"), choices=["yellow", "green"], help="Taxi data colour (yellow or green)")
#     parser.add_argument("--year", required=True, type=int, help="Year of the data to load")
#     parser.add_argument("--month", required=True, type=int, help="Month of the data to load (1-12)")

#     args = parser.parse_args()
#     load_nytaxi_data(args)



import os
import argparse
import pandas as pd
from sqlalchemy import create_engine
import wget
from time import time

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port 
    db = params.db
    table_name = params.table_name
    url = params.url
    
    # Standardizing file naming
    if url.endswith('.csv.gz'):
        file_name = 'output.csv.gz'
    elif url.endswith('.csv'):
        file_name = 'output.csv'
    else:
        file_name = 'output.parquet'

    # 1. Download the file
    print(f"Downloading {url}...")
    #os.system(f"wget {url} -O {file_name}")
    wget.download(url, file_name)

    # 2. Setup Database Connection
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # 3. Decision Logic: How to read the file?
    print(f"Processing {file_name}...")
    
    if file_name.endswith('.parquet'):
        # Parquet files are read in full; split into chunks for the DB loop
        df = pd.read_parquet(file_name)
        chunks = [df[i:i+100000] for i in range(0, df.shape[0], 100000)]
    else:
        # CSV files use the iterator pattern
        # Decision: Using 'low_memory=False' to avoid DtypeWarnings on large files
        df_iter = pd.read_csv(file_name, iterator=True, chunksize=100000, low_memory=False)
        chunks = df_iter

    # 4. The Unified Ingestion Loop
    for i, df_chunk in enumerate(chunks):
        t_start = time()

        # Clean datetime columns (standardizes column names across 2021/2025 data)
        for col in df_chunk.columns:
            if 'datetime' in col.lower() or 'pickup' in col.lower() or 'dropoff' in col.lower():
                df_chunk[col] = pd.to_datetime(df_chunk[col])

        # Insert into Postgres
        # Decision: Use 'append' to support multiple months and Zone lookups
        df_chunk.to_sql(name=table_name, con=engine, if_exists='append', index=False)

        t_end = time()
        print(f'Inserted chunk {i+1}, took %.3f second' % (t_end - t_start))

    print("Finished ingesting data into the postgres database")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV/Parquet data to Postgres')
    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--table_name', help='name of the table where we will write the results to')
    parser.add_argument('--url', help='url of the csv or parquet file')

    args = parser.parse_args()
    main(args)