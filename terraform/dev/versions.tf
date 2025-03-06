terraform {
  backend "s3" {
    bucket = "rsde-smsi-vr-terraform-backend"
    key    = "terraform/terraform.tfstate"
    region = "ca-central-1"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.87.0"
    }
  }
}

provider "aws" {
  region = "ca-central-1"
  default_tags {
    tags = {
      Environment = "dev"
      ManagedBy   = "Terraform"
      Project     = "smsi2"
    }
  }
}