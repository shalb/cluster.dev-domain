resource "aws_dynamodb_table" "dns-manager" {
  name           = "dns-manager"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "ID"
  stream_enabled = false

  attribute {
    name = "ID"
    type = "S"
  }

  point_in_time_recovery {
    enabled = false
  }

  ttl {
    attribute_name = ""
    enabled        = false
  }

  tags = {
    Creator = "cluster.dev"
  }
}
