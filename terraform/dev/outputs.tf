output "changedetection_url" {
  description = "The URL to access the ChangeDetection.io instance"
  value       = module.changedetection.changedetection_url
}

output "efs_id" {
  description = "The ID of the EFS file system storing ChangeDetection data"
  value       = module.changedetection.efs_id
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster running ChangeDetection"
  value       = module.changedetection.ecs_cluster_name
}

output "vpc_id" {
  description = "The ID of the VPC containing the ChangeDetection deployment"
  value       = module.changedetection.vpc_id
}