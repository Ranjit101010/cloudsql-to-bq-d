variable "project_id" {
  type        = string
  description = "the gcp project id"
}

variable "region" {
  type        = string
  description = "the region of the project"
}

variable "tf_state_bucket" {
  type        = string
  description = "the bucket which is used to store the terraform state files"
}

variable "bucket" {
  type = map(object({
    name                        = string
    storage                     = string
    force_destroy               = bool
    public_access_prevention    = string
    enabled                     = bool
    uniform_bucket_level_access = bool
  }))
}

variable "bucket_object" {
  type = map(object({
    name    = string # folder name should end with '/'
    content = string # content is ignored but should be non-empty      
  }))
}

variable "zip-data" {
  type = map(object({
    file_type   = string
    output_path = string
    source_dir  = string
  }))
}


variable "gcp_functions" {
  type = map(object({

    name               = string
    description        = string
    runtime            = string
    entry_point        = string # Set the entry point
    max_instance_count = number
    available_memory   = string
    timeout_seconds    = number
    event_type         = string
    attribute          = string
  }))
}

variable "datasets" {
  type = map(object({
    dataset_id                  = string
    friendly_name               = string
    description                 = string
    default_table_expiration_ms = number
  }))
}

variable "stg_tables" {
  type = map(object({
    name                = string
    deletion_protection = bool
  }))
}

variable "srv_tables" {
  type = map(object({
    name                = string
    deletion_protection = bool
    schema              = string
  }))
}

variable "routines" {
  type = map(object({
    routine_id      = string
    routine_type    = string
    definition_body = string
    language        = string
  }))
}


variable "gcp_workflows" {
  type = map(object({
    name                  = string
    description           = string
    source_contents       = string
    service_account_email = string
  }))

}

variable "bucket_notifications" {
  type = object({
    payload_format = string
    event_types    = list(string)
  })
}

variable "pubsub_topic" {
  type = object({
    name = string
  })
}
