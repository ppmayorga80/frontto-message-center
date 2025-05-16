variable "project_id" {
  default = "sistemap-msg"
}

variable "region" {
  default = "us-central1"
}

variable "frontto_domain" {
  default = "hello"
}

variable "fn_name" {
  default = "helloworld"
}

variable "timeout" {
  default = 60
}

variable "max_instances" {
  default = 1 #TODO: reduce this value to 500
}

variable "memory" {
  default = "128Mi"
}

variable "cpu" {
  default = "1"
}