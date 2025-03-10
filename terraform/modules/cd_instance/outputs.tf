output "changedetection_url" {
  description = "The URL to access the ChangeDetection.io instance"
  value       = "http://${aws_lb.changedetection_lb.dns_name}"
}

output "efs_id" {
  description = "The ID of the EFS file system storing ChangeDetection data"
  value       = aws_efs_file_system.changedetection_data.id
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster running ChangeDetection"
  value       = aws_ecs_cluster.changedetection_cluster.name
}

output "ecs_service_name" {
  description = "The name of the ECS service running ChangeDetection"
  value       = aws_ecs_service.changedetection_service.name
}

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.changedetection_vpc.id
}

output "security_groups" {
  description = "Security groups for the deployment"
  value = {
    loadbalancer = aws_security_group.changedetection_lb_sg.id
    ecs          = aws_security_group.changedetection_ecs_sg.id
    efs          = aws_security_group.changedetection_efs_sg.id
  }
}