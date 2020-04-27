variable "region" {
  type        = string
  default     = "eu-central-1"
  description = "The AWS region."
}

variable "dynamodb_table_backend" {
  type        = string
  default     = "dns-manager-state"
  description = "Dynamodb table, which needed for s3 backend bucket"
}
