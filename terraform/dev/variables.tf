variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ca-central-1"
}

variable "whitelist_ips" {
  description = "Your IP address in CIDR notation (e.g., 123.123.123.123/32) to whitelist for access"
  type        = list(string)
  sensitive   = true
  default     = []
}

variable "disk_size_gb" {
  description = "Size of the EFS file system in GB"
  type        = number
  default     = 10
}
