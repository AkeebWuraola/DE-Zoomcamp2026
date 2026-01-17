#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

#Parameterize the script


#Specify datatypes for each column
datatypes = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

def run():
    pg_user = 'root'
    pg_password = input()
    pg_host = 'localhost'
    pg_port = 5432
    pg_db = input()

    year = 2021
    month = 1
    target_table = 'yellow_taxi_data' #specify table name to be created on the db
    chunksize = 100000 #specify chunksize for db load

    #https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/yellow/   - dataset link
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow'
    url = f'{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz'

    # engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
    engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')

    #load database in chunks
    df_iterator = pd.read_csv(url,  dtype=datatypes,   parse_dates=parse_dates, iterator = True, chunksize = chunksize)
    
    first = True
    #Load data per chunk
    for df in tqdm(df_iterator):
        if first:
            #pandas created a table with the structure of the data df
            df.head(n=0).to_sql(name= target_table, con=engine, if_exists='replace')
            first = False
            
        df.to_sql(name=target_table, con=engine, if_exists='append')

if __name__== '__main__':
    run()

    #since you parameterized input, you have to input the variables in your command line
    