resource "google_storage_bucket" "buckets" {
  for_each                    = var.bucket
  name                        = each.value.name
  location                    = var.region
  storage_class               = each.value.storage
  force_destroy               = each.value.force_destroy
  public_access_prevention    = each.value.public_access_prevention
  uniform_bucket_level_access = each.value.uniform_bucket_level_access
  versioning {
    enabled = each.value.enabled
  }
}


resource "google_storage_bucket_object" "empty_folder" {
  for_each   = var.bucket_object
  name       = each.value.name    # folder name should end with '/'
  content    = each.value.content # content is ignored but should be non-empty
  bucket     = google_storage_bucket.buckets["bucket-gcs-to-bq-d"].name
  depends_on = [google_storage_bucket.buckets["bucket-gcs-to-bq-d"]]
}