data "archive_file" "source" {
  type        = "zip"
  source_dir  = "../src"
  output_path = "./tmp/function.zip"
}

resource "google_storage_bucket_object" "zip" {
  source       = data.archive_file.source.output_path
  content_type = "application/zip"
  name         = "function-src-${data.archive_file.source.output_md5}.zip"
  bucket       = google_storage_bucket.function_bucket.name
  depends_on = [
    google_storage_bucket.function_bucket,
    data.archive_file.source
  ]
}

resource "google_cloudfunctions2_function" "function" {
  name        = "${var.frontto_domain}_${var.fn_name}"
  location    = var.region
  description = ""

   # Bind the service account here!

  build_config {
    runtime     = "python310"
    entry_point = "whatsapp_webhook"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.zip.name
      }
    }
  }

  service_config {
    service_account_email = google_service_account.my_service_account.email

    # ✅ Define your environment variables here
    environment_variables = {
      PROJECT_ID = var.project_id
    }


    min_instance_count               = 0
    max_instance_count               = var.max_instances
    max_instance_request_concurrency = 1
    available_memory                 = var.memory
    available_cpu                    = var.cpu
    timeout_seconds                  = var.timeout
    ingress_settings                 = "ALLOW_ALL"
    all_traffic_on_latest_revision   = true
  }

}
