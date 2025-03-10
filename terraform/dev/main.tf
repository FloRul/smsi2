module "changedetection" {
  source = "../modules/cd_instance"
  
  aws_region     = var.aws_region
  whitelist_ips  = var.whitelist_ips
  disk_size_gb   = var.disk_size_gb
}