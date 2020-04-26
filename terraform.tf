terraform {
  backend "s3" {
    bucket = "dns-manager-state"
    key    = "state"
    region = "eu-central-1"
  }
  required_providers {
    aws = "~> 2.23"
  }
}
