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