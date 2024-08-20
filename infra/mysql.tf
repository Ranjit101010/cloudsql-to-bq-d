
# resource "google_sql_database_instance" "my_instance" {
#   name             = "cloudsql-to-bq-instance-d"
#   database_version = "MYSQL_8_0"
#   region           = var.region

#   settings {
#     tier      = "db-f1-micro" # Custom instance type with 1 vCPU and ~628.74 MB RAM
#     edition   = "ENTERPRISE"
#     disk_size = 10
#     disk_type = "PD_HDD"
#     data_cache_config {
#       data_cache_enabled = false
#     }
#     ip_configuration {
#       authorized_networks {
#         name  = "public-ip"
#         value = "0.0.0.0/0" # Allows connections from anywhere
#       }
#       ipv4_enabled = true # Enable public IP
#     }

#     backup_configuration {
#       enabled                        = true
#       binary_log_enabled             = true # Enable point-in-time recovery
#       start_time                     = "03:00" # Automated backup start time   
#       location                       = var.region
#     }
#   }
#   root_password       = "101010" # Set your root password
#   deletion_protection = false    # Set to true if you want to prevent accidental deletion
# }

# resource "google_sql_database" "database_name" {
#   name     = "customers"
#   instance = google_sql_database_instance.my_instance.name
# }

# resource "google_sql_user" "database_user" {
#   name     = "root"
#   instance = google_sql_database_instance.my_instance.name
#   password = "101010" # Set a secure password for the user
# }
