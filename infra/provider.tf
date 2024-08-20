terraform {
  backend "gcs" {
    bucket = "bucket-terraform-cloudsql-to-bq-d"
    prefix = "terraform/state"
  }
}
