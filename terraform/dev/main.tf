module "cd_lightail_instance" {
  source = "../modules/cd_instance"
  aws_region = var.aws_region
  whitelist_ips = var.whitelist_ips
}