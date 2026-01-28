# NYC Taxi Data Lakehouse 🚕

This project is a comprehensive Data Engineering pipeline built during the [2026 Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp). It follows a modular architecture designed for scalability, security, and observability, transitioning from local processing to a cloud-native Lakehouse.

---

## 🗺️ Project Roadmap & Modules

### 📦 Module 1: Containerization & Infrastructure (Complete)
**Goal:** Provision a reproducible environment and cloud landing zone using Infrastructure as Code (IaC).

* **Tech Stack:** Docker, Terraform, GCP (GCS & BigQuery).
* **Production-Grade Decisions:**
    * **IaC over Click-Ops:** Used Terraform to manage GCP resources. *Trade-off:* Higher initial setup time, but ensures environment parity and prevents "configuration drift."
    * **UBLA Compliance:** Implemented `uniform_bucket_level_access = true`. *Trade-off:* Disables legacy fine-grained ACLs in favor of modern, centralized IAM-based access control.
    * **State Management:** Strictly excluded `.tfstate` and database binaries from version control using a robust `.gitignore` to prevent credential leakage and repo bloat.

### 🤖 Module 2: Workflow Orchestration (In-Progress)
**Goal:** Automate and observe data movement from local/web sources to the Data Lake.

* **Tech Stack:** Kestra, Python, YAML.
* **Production-Grade Decisions:**
    * **Declarative Orchestration:** Moving from manual Python scripts to Kestra YAML flows. *Trade-off:* Adds the overhead of an orchestrator, but provides built-in retries, scheduling, and execution history.
    * **Hive Partitioning:** Structuring GCS paths as `green/YYYY/MM/data.parquet`. *Trade-off:* Requires specific folder logic during ingestion, but drastically reduces BigQuery scan costs and improves query performance.

### 🏛️ Module 3: Data Warehousing (Upcoming)
**Goal:** Efficiently query and model data within the Warehouse.
* **Concepts:** Partitioning, Clustering, and External Tables in BigQuery.

---

## 🛠️ How to Run Modules

### 1. Prerequisites
* GCP Account with a linked Billing Account.
* `gcloud` CLI installed and authenticated (`gcloud auth application-default login`).
* `uv` installed for Python dependency management.

### 2. Infrastructure (Module 1)
```bash
cd terraform
terraform init
terraform plan
terraform apply