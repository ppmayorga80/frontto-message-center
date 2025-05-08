# terraform {
#   backend "local" {}
# }

terraform {
  backend "gcs" {
    bucket = "fn-frontto-whatsapp-terraform"
    prefix = "terraform/state"
  }
}