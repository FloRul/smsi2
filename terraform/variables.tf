variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "whitelist_ip" {
  description = "Your IP address in CIDR notation (e.g., 123.123.123.123/32) to whitelist for access"
  type        = string
  sensitive   = true
}