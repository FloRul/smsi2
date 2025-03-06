output "changedetection_instance_ip" {
  description = "Public IP address of the ChangeDetection.io instance"
  value       = aws_lightsail_static_ip.changedetection_static_ip.ip_address
}

output "changedetection_url" {
  description = "URL to access ChangeDetection.io"
  value       = "http://${aws_lightsail_static_ip.changedetection_static_ip.ip_address}:5000"
}