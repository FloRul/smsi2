output "changedetection_instance_ip" {
  description = "Public IP address of the ChangeDetection.io instance"
  value       = module.cd_lightail_instance.public_ip_address
}

output "changedetection_url" {
  description = "URL to access ChangeDetection.io"
  value       = "http://${module.cd_lightail_instance.public_ip_address}:5000"
}
