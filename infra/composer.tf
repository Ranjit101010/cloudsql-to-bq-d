
resource "google_composer_environment" "cloudsql_to_bq_composer" {
  name     = "cloudsql-to-bq-dags-d"
  region   = var.region

  config {

    software_config {
      image_version = "composer-3-airflow-2"
    }


    workloads_config {
      scheduler {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
        count      = 1
      }
      triggerer {
        cpu       = 0.5
        memory_gb = 1
        count     = 1
      }
      web_server {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
      }
      worker {
        cpu        = 0.5
        memory_gb  = 2
        storage_gb = 1
        min_count  = 1
        max_count  = 3
      }

    }
    environment_size = "ENVIRONMENT_SIZE_SMALL"

    node_config {
      service_account = "github-actions@cloudsql-to-bq-d.iam.gserviceaccount.com"
    }

  }
}