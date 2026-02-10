-- Create external table from GCS parquet files
CREATE OR REPLACE EXTERNAL TABLE `nytaxi-485607.nytaxi_data.yellow_tripdata_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://nytaxi-485607-yellow_taxi/raw/yellow_tripdata_2024-*.parquet']
);
