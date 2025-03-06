output "changedetection_instance_ip" {
  description = "Public IP address of the ChangeDetection.io instance"
  value       = module.cd_lightail_instance.changedetection_instance_ip
}

output "changedetection_url" {
  description = "URL to access ChangeDetection.io"
  value       = "http://${module.cd_lightail_instance.changedetection_instance_ip}:5000"
}
