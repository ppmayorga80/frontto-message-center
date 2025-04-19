variable "project_id" {
  default = "frontto-message-center"
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
  default = "256Mi"
}

variable "cpu" {
  default = "1"
}


#---- ENV VARIABLES
variable "llm_platform" {
  default = "openai"
}
variable "llm_model" {
  default = "gpt-4o-mini"
}
variable "llm_prompt_path" {
  default = "gs://fn-frontto-whatsapp/prompts/openai-latest.md"
}

variable "messages_path_fmt" {
  default = "gs://fn-frontto-whatsapp/messages/{phone}.jsonl"
}
