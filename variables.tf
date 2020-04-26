variable "region" {
  type        = string
  default     = "eu-central-1"
  description = "The AWS region."
}

variable "s3_backend_bucket" {
  type        = string
  default     = "dns-manager-state"
  description = "The s3 backend bucket"
}
