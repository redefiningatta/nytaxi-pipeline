variable "credentials" {
  description = "My Credentials"
  default     = "./keys/my-creds.json" # Decision: Path to your JSON key
}

variable "project" {
  description = "Project"
  default     = "nytaxi-485607"
}

variable "region" {
  description = "Region"
  default     = "europe-west1"
}

variable "location" {
  description = "Project Location"
  default     = "europe-west1"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  default     = "nytaxi_kestra_data_lake" # Must be globally unique!
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  default     = "nytaxi_kestra_data"
}