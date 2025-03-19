# Create a Service Account
resource "google_service_account" "my_service_account" {
  account_id   = "cf-${var.frontto_domain}-${var.fn_name}"
  display_name = "My Service Account for ${var.frontto_domain}-${var.fn_name}"
}

# Grant Storage Admin Role (Full Access to Buckets & Objects)
resource "google_project_iam_member" "storage_access" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.my_service_account.email}"
}

# Grant Secret Manager Secret Accessor Role (Read Secret Values)
resource "google_project_iam_member" "secret_manager_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.my_service_account.email}"
}

resource "google_cloudfunctions2_function_iam_member" "allow_unauthenticated" {
  project        = var.project_id
  location       = var.region
  cloud_function = google_cloudfunctions2_function.function.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}
