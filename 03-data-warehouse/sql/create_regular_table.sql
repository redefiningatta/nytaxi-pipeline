-- Create regular (materialized) table from external table
CREATE OR REPLACE TABLE `nytaxi-485607.nytaxi_data.yellow_tripdata` AS
SELECT * FROM `nytaxi-485607.nytaxi_data.yellow_tripdata_external`;
