output "function_uri" {
  value = google_cloudfunctions2_function.function.service_config[0].uri
}

# Output the service account email for use in function.tf
output "function_service_account_email" {
  value       = google_service_account.function_sa.email
  description = "Email of the service account created for the Cloud Function"
}

output "project_id" {
  value = var.project_id
}
