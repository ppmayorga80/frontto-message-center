resource "google_storage_bucket" "function_bucket" {
  name     = "function_${var.frontto_domain}_${var.fn_name}"
  location = var.region
}