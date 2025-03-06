variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  nullable    = false
}

variable "whitelist_ips" {
  description = "Your IP address in CIDR notation (e.g., 123.123.123.123/32) to whitelist for access"
  type        = list(string)
  sensitive   = true
  nullable    = false
}
