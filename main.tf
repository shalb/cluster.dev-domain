provider "aws" {
}

resource "aws_dynamodb_table" "terraform_state_lock" {
  name           = "${var.dynamodb_table_backend}"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

