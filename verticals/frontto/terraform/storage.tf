resource "google_storage_bucket" "function_bucket" {
  name     = "fn-bucket-${var.frontto_domain}-${var.fn_name}-${random_id.bucket_suffix.hex}"
  location = var.region
  force_destroy = true
  uniform_bucket_level_access = true
  public_access_prevention = "enforced"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}
