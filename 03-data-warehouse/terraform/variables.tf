
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
  default     = "nytaxi-485607-yellow_taxi" # Must be globally unique!
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}
