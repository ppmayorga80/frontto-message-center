variable "project_id" {
  default = "sistemap-msg"
}

variable "region" {
  default = "us-central1"
}

variable "frontto_domain" {
  default = "frontto"
}

variable "fn_name" {
  default = "whatsapp"
}

variable "timeout" {
  default = 60
}

variable "max_instances" {
  default = 1
}

variable "memory" {
  default = "128Mi"
}

variable "cpu" {
  default = "1"
}

#---- ENV VARIABLES
variable "llm_prompt_path" {
  default = "gs://frontto-whatsapp/prompts/openai-latest.md"
}