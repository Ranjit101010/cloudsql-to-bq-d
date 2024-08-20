resource "google_bigquery_dataset" "customers_dataset" {
  for_each                    = var.datasets
  dataset_id                  = each.value.dataset_id
  friendly_name               = each.value.friendly_name
  description                 = each.value.description
  location                    = var.region
  default_table_expiration_ms = each.value.default_table_expiration_ms
}

resource "google_bigquery_table" "customers_stg_table" {
  for_each            = var.stg_tables
  dataset_id          = google_bigquery_dataset.customers_dataset["stg_dataset"].dataset_id
  table_id            = each.value.name
  deletion_protection = each.value.deletion_protection
}

resource "google_bigquery_table" "customers_srv_table" {
  for_each            = var.srv_tables
  dataset_id          = google_bigquery_dataset.customers_dataset["srv_dataset"].dataset_id
  table_id            = each.value.name
  deletion_protection = each.value.deletion_protection
  schema              = file(each.value.schema)
}

# resource "google_bigquery_routine" "staging_to_serving" {
#   for_each     = var.routines
#   dataset_id   = google_bigquery_dataset.customers_dataset["stg_dataset"].dataset_id
#   routine_id   = each.value.routine_id
#   routine_type = each.value.routine_type
#   definition_body = templatefile("${path.module}/${each.value.definition_body}", { "project_id" = var.project_id,
#   "staging_dataset_id" = google_bigquery_dataset.customers_dataset["stg_dataset"].dataset_id })
#   language = each.value.language
# }