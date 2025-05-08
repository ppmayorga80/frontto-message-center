# iam.tf

# Create a dedicated service account for the Cloud Function
resource "google_service_account" "function_sa" {
  project      = var.project_id
  account_id   = "${var.frontto_domain}-${var.fn_name}-sa" # Unique service account ID
  display_name = "${var.frontto_domain} ${var.fn_name} Function Service Account"
}

# TODO: Add bucket level permission
# # Grant Storage Object Admin role to the service account on the function bucket
# resource "google_storage_bucket_iam_member" "function_sa_storage_access" {
#   bucket   = google_storage_bucket.function_bucket.name # Assuming your bucket is defined in function.tf
#   role     = "roles/storage.objectAdmin" # Grant Object Admin for broad access
#   member   = "serviceAccount:${google_service_account.function_sa.email}"
# }

# Grant Storage Admin Role (Full Access to Buckets & Objects)
resource "google_project_iam_member" "storage_access" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

# Grant Secret Manager Secret Accessor Role (Read Secret Values)
resource "google_project_iam_member" "secret_manager_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

resource "google_cloudfunctions2_function_iam_member" "allow_unauthenticated" {
  project        = var.project_id
  location       = var.region
  cloud_function = google_cloudfunctions2_function.function.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}
