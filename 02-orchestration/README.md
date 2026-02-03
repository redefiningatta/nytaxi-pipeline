# NYC Taxi Data Pipeline: Orchestration Layer (Kestra)

## Project Overview
This project automates the end-to-end ingestion of the NYC Taxi (Yellow and Green) dataset into a Google Cloud Platform (GCP) Data Lakehouse. Using **Kestra** as the orchestrator, the pipeline handles data extraction, storage in GCS, and transformation/loading into BigQuery.



## Architecture Decisions
* **Orchestration:** Kestra (Standalone) running via Docker Compose on WSL2.
* **Authentication:** Utilized **Application Default Credentials (ADC)** via Docker volume mounting for secure, production-grade access to GCP resources without hardcoding JSON keys.
* **Storage:** Google Cloud Storage (GCS) serves as the Bronze/Landing layer.
* **Warehouse:** Google BigQuery serves as the Silver layer, utilizing **Partitioned Tables** (by day) and **Clustered Columns** for cost-efficient querying.
* **Idempotency:** Implemented `MERGE` statements with `MD5` hashing for surrogate keys (`unique_row_id`) to ensure that backfills do not create duplicate records.

## Setup & Infrastructure
### Docker Configuration
The Kestra instance is configured to bridge the host's GCloud credentials into the container:
```yaml
