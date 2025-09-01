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

variable "disk_size_gb" {
  description = "Size of the detachable disk in GB"
  type        = number
  default     = 8
  nullable    = false
}

variable "backup_schedule" {
  description = "the schedule to proceed to backup the changedetection instance"
  type        = string
  default     = "cron(0 1 * * ? *)"
  nullable    = false
}

variable "backup_retention_period" {
  description = "the retention period of the changedetection instance backup (in days)"
  type        = number
  default     = 30
}
