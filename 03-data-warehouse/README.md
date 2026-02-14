# Module 3 Homework: Data Warehousing & BigQuery

**Student:** Peter Omondi  
**Email:** redefiningatta@gmail.com  
**GitHub:** [nytaxi-pipeline](https://github.com/redefiningatta/nytaxi-pipeline)

---

## Table of Contents
- [Overview](#overview)
- [Setup](#setup)
- [Data Loading](#data-loading)
- [BigQuery Tables](#bigquery-tables)
- [Homework Questions](#homework-questions)
- [Project Structure](#project-structure)

---

## Overview

This homework demonstrates data warehousing concepts using Google Cloud Platform:
- **Data Source:** NYC Yellow Taxi Trip Records (January - June 2024)
- **Storage:** Google Cloud Storage (Data Lake)
- **Warehouse:** Google BigQuery
- **Infrastructure:** Terraform
- **Data Pipeline:** Python with UV package manager

**Dataset Stats:**
- Total Records: 20,332,093
- Time Period: January 2024 - June 2024 (6 months)
- File Format: Parquet
- Storage Location: `gs://nytaxi-485607-yellow_taxi/raw/`

---

## Setup

### Prerequisites
```bash
# Required tools
- Terraform >= 1.0
- Google Cloud SDK (gcloud)
- Python 3.x
- UV package manager
- bq command line tool
```

### 1. Infrastructure Deployment (Terraform)

Navigate to terraform directory and deploy:
```bash
cd 03-data-warehouse/terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Apply infrastructure
terraform apply
```

**Resources Created:**
- GCS Bucket: `nytaxi-485607-yellow_taxi`
- BigQuery Dataset: `nytaxi_data`
- Location: `europe-west1`

### 2. Authentication
```bash
# Login to Google Cloud
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project nytaxi-485607
```

---

## Data Loading

### Download and Upload to GCS

The Python script downloads 6 months of Yellow Taxi data and uploads to GCS:
```bash
cd 03-data-warehouse/data-loader

# Run with UV (automatically manages dependencies)
uv run load_yellow_taxi_data.py
```

**Script Features:**
- Downloads parquet files from NYC TLC
- Uploads to GCS bucket under `raw/` folder
- Cleans up local files after upload
- Verifies all files uploaded successfully

**Files Loaded:**
```
gs://nytaxi-485607-yellow_taxi/raw/
├── yellow_tripdata_2024-01.parquet
├── yellow_tripdata_2024-02.parquet
├── yellow_tripdata_2024-03.parquet
├── yellow_tripdata_2024-04.parquet
├── yellow_tripdata_2024-05.parquet
└── yellow_tripdata_2024-06.parquet
```

### Verification
```bash
# List files in GCS
gsutil ls gs://nytaxi-485607-yellow_taxi/raw/

# Expected output: 6 parquet files
```

---

## BigQuery Tables

### 1. External Table

Creates a table that references data in GCS:
```sql
CREATE OR REPLACE EXTERNAL TABLE `nytaxi-485607.nytaxi_data.yellow_tripdata_external`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://nytaxi-485607-yellow_taxi/raw/yellow_tripdata_2024-*.parquet']
);
```

**Execute:**
```bash
bq query --use_legacy_sql=false < sql/create_external_table.sql
```

### 2. Regular (Materialized) Table

Creates a native BigQuery table with data copied from external table:
```sql
CREATE OR REPLACE TABLE `nytaxi-485607.nytaxi_data.yellow_tripdata` AS
SELECT * FROM `nytaxi-485607.nytaxi_data.yellow_tripdata_external`;
```

**Execute:**
```bash
bq query --use_legacy_sql=false < sql/create_regular_table.sql
```

### 3. Optimized Table (Partitioned & Clustered)

Creates an optimized table for queries filtering by dropoff datetime and ordering by VendorID:
```sql
CREATE OR REPLACE TABLE `nytaxi-485607.nytaxi_data.yellow_tripdata_optimized`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS
SELECT * FROM `nytaxi-485607.nytaxi_data.yellow_tripdata`;
```

**Execute:**
```bash
bq query --use_legacy_sql=false < sql/create_optimized_table.sql
```

### Verify Tables
```bash
# List tables in dataset
bq ls nytaxi_data

# Check row counts
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata_external\`"
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata\`"
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata_optimized\`"
```

**Expected:** All tables should have **20,332,093 rows**

---

## Homework Questions

### Question 1: Data Storage Location

**Q: Where is the data stored in the External Table you created?**

**Answer:** Google Cloud Storage (GCS)

**Location:** `gs://nytaxi-485607-yellow_taxi/raw/`

**Explanation:**
- External tables store only metadata and schema in BigQuery
- Actual data remains in the source location (GCS parquet files)
- BigQuery queries the files in-place without copying data

**Verification:**
```bash
gsutil ls gs://nytaxi-485607-yellow_taxi/raw/
```

---

### Question 2: Estimated Data Scan

**Q: What is the estimated amount of data that will be read when executing `COUNT(DISTINCT PULocationID)` on both tables?**

**Query:**
```sql
-- External Table
SELECT COUNT(DISTINCT PULocationID) as distinct_pickup_locations 
FROM `nytaxi-485607.nytaxi_data.yellow_tripdata_external`;

-- Regular Table
SELECT COUNT(DISTINCT PULocationID) as distinct_pickup_locations 
FROM `nytaxi-485607.nytaxi_data.yellow_tripdata`;
```

**Answer:** **0 MB for External Table and 155.12 MB for Regular Table**

**Testing:**
```bash
# External Table - dry run
bq query --use_legacy_sql=false --dry_run \
"SELECT COUNT(DISTINCT PULocationID) FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata_external\`"

# Regular Table - dry run
bq query --use_legacy_sql=false --dry_run \
"SELECT COUNT(DISTINCT PULocationID) FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata\`"
```

**Results:**
- External Table: `0 bytes` (lower bound - cannot estimate before execution)
- Regular Table: `162,656,744 bytes` ≈ **155.12 MB**

**Explanation:**
- **External Table (0 MB):** BigQuery cannot accurately estimate costs for external tables before query execution. The actual cost is determined at runtime when scanning the parquet files.
- **Regular Table (155.12 MB):** BigQuery can precisely estimate because data is stored in native columnar format. It knows exactly which column will be scanned (only `PULocationID`).

**Key Learning:**
- External tables: Lower storage cost, unpredictable query cost
- Native tables: Storage cost, but optimized and predictable query performance

---

### Question 3: Distinct PULocationID Count

**Q: How many records have a PULocationID of 0?**

**Query:**
```sql
SELECT COUNT(*) as records_with_zero_location
FROM `nytaxi-485607.nytaxi_data.yellow_tripdata`
WHERE PULocationID = 0;
```

**Execute:**
```bash
bq query --use_legacy_sql=false \
"SELECT COUNT(*) as records_with_zero_location 
FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata\`
WHERE PULocationID = 0"
```

---

### Question 4: Optimization Strategy

**Q: What is the best strategy to optimize a table if queries always filter by `tpep_dropoff_datetime` and order by `VendorID`?**

**Answer:** 
- **PARTITION BY** `DATE(tpep_dropoff_datetime)`
- **CLUSTER BY** `VendorID`

**Implementation:**
```sql
CREATE OR REPLACE TABLE `nytaxi-485607.nytaxi_data.yellow_tripdata_optimized`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID
AS
SELECT * FROM `nytaxi-485607.nytaxi_data.yellow_tripdata`;
```

**Why This Works:**
1. **Partitioning by date:** 
   - Only scans partitions matching the date filter
   - Massive cost reduction (only reads relevant days)
   - Each partition contains one day of data

2. **Clustering by VendorID:**
   - Data is physically sorted by VendorID within each partition
   - Speeds up ORDER BY operations
   - Improves filtering on VendorID
   - No additional cost

**Performance Comparison:**
```bash
# Test query
QUERY="SELECT DISTINCT VendorID 
FROM TABLE_NAME
WHERE tpep_dropoff_datetime >= '2024-03-01' 
  AND tpep_dropoff_datetime < '2024-03-16'"

# Non-optimized
bq query --use_legacy_sql=false --dry_run \
"SELECT DISTINCT VendorID FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata\`
WHERE tpep_dropoff_datetime >= '2024-03-01' AND tpep_dropoff_datetime < '2024-03-16'"

# Optimized
bq query --use_legacy_sql=false --dry_run \
"SELECT DISTINCT VendorID FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata_optimized\`
WHERE tpep_dropoff_datetime >= '2024-03-01' AND tpep_dropoff_datetime < '2024-03-16'"
```

**Expected Result:** Optimized table scans significantly less data (only 15 days of partitions vs entire 6 months)

---

### Question 5: Count(`*`) vs COUNT(column)

**Q: Why does `SELECT COUNT(*)` estimate 0 bytes?**

**Query:**
```sql
SELECT COUNT(*) FROM `nytaxi-485607.nytaxi_data.yellow_tripdata`;
```

**Answer:** BigQuery stores row count in table metadata

**Comparison:**
```bash
# COUNT(*) - uses metadata (0 bytes)
bq query --use_legacy_sql=false --dry_run \
"SELECT COUNT(*) FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata\`"

# COUNT(column) - must scan column (~155 MB)
bq query --use_legacy_sql=false --dry_run \
"SELECT COUNT(PULocationID) FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata\`"

# COUNT(DISTINCT column) - must scan and deduplicate (~155 MB)
bq query --use_legacy_sql=false --dry_run \
"SELECT COUNT(DISTINCT PULocationID) FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata\`"
```

**Explanation:**
- `COUNT(*)`: Uses table metadata (0 bytes)
- `COUNT(column)`: Must scan column to check for NULLs
- `COUNT(DISTINCT column)`: Must scan and process unique values

**Best Practice:** Always use `COUNT(*)` when you just need total row count!

---

## Project Structure
```
03-data-warehouse/
├── terraform/
│   ├── main.tf                      # GCS bucket and BQ dataset
│   ├── variables.tf                 # Configuration variables
│   └── README.md
│
├── data-loader/
│   ├── load_yellow_taxi_data.py     # Data loading script
│   ├── pyproject.toml               # UV dependencies
│   └── uv.lock
│
├── sql/
│   ├── create_external_table.sql    # External table DDL
│   ├── create_regular_table.sql     # Regular table DDL
│   └── create_optimized_table.sql   # Partitioned & clustered table
│
├── homework/
│   └── README.md                     # This file
│
└── README.md                         # Main project README
```

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **Terraform** | Infrastructure as Code (IaC) |
| **Google Cloud Storage** | Data Lake (object storage) |
| **BigQuery** | Data Warehouse (analytics) |
| **Python** | Data pipeline scripting |
| **UV** | Fast Python package manager |
| **Parquet** | Columnar data format |
| **gcloud CLI** | GCP management |
| **bq CLI** | BigQuery management |

---

## Key Learnings

### 1. External vs Native Tables
- **External:** Lower cost, data stays in GCS, unpredictable query performance
- **Native:** Optimized storage, predictable costs, better performance

### 2. Partitioning & Clustering
- **Partition:** Divide data by date/timestamp (reduces data scanned)
- **Cluster:** Sort data within partitions (improves filtering/sorting)

### 3. Cost Optimization
- Use `COUNT(*)` instead of `COUNT(column)`
- Partition large tables by date
- Cluster by frequently filtered/sorted columns
- Use columnar formats (Parquet)

### 4. BigQuery Best Practices
- Always use `--dry_run` to estimate costs
- Partition tables with > 1GB data
- Cluster by high-cardinality columns
- Avoid `SELECT *` in production

---

## Verification Commands
```bash
# Check infrastructure
terraform show

# List GCS files
gsutil ls -lh gs://nytaxi-485607-yellow_taxi/raw/

# List BigQuery tables
bq ls nytaxi_data

# Show table schema
bq show --schema nytaxi_data.yellow_tripdata_optimized

# Query table info
bq show nytaxi_data.yellow_tripdata_optimized

# Sample data
bq query --use_legacy_sql=false \
"SELECT * FROM \`nytaxi-485607.nytaxi_data.yellow_tripdata\` LIMIT 5"
```

---

## Cleanup (Optional)
```bash
# Delete BigQuery tables
bq rm -f nytaxi_data.yellow_tripdata_external
bq rm -f nytaxi_data.yellow_tripdata
bq rm -f nytaxi_data.yellow_tripdata_optimized

# Delete dataset
bq rm -r -f nytaxi_data

# Delete GCS files
gsutil -m rm -r gs://nytaxi-485607-yellow_taxi/raw/

# Destroy Terraform resources
cd terraform
terraform destroy
```

---

## References

- [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery Partitioning](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [BigQuery Clustering](https://cloud.google.com/bigquery/docs/clustered-tables)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

---

**Submission Date:** February 2, 2026  
**Course:** Data Engineering Zoomcamp - Module 3