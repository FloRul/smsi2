resource "aws_cloudwatch_dashboard" "changedetection_dashboard" {
  dashboard_name = "ChangeDetection-Dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", aws_ecs_service.changedetection_service.name, "ClusterName", aws_ecs_cluster.changedetection_cluster.name]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "ECS CPU Utilization"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ServiceName", aws_ecs_service.changedetection_service.name, "ClusterName", aws_ecs_cluster.changedetection_cluster.name]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "ECS Memory Utilization"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "HealthyHostCount", "TargetGroup", aws_lb_target_group.changedetection_tg.arn_suffix, "LoadBalancer", aws_lb.changedetection_lb.arn_suffix]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "ELB Healthy Host Count"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", aws_lb.changedetection_lb.arn_suffix]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "ELB Request Count"
        }
      }
    ]
  })
}

resource "aws_cloudwatch_metric_alarm" "changedetection_cpu_alarm" {
  alarm_name          = "changedetection-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors ecs cpu utilization"
  alarm_actions       = []
  ok_actions          = []

  dimensions = {
    ClusterName = aws_ecs_cluster.changedetection_cluster.name
    ServiceName = aws_ecs_service.changedetection_service.name
  }

  tags = {
    Name = "changedetection-cpu-alarm"
  }
}

resource "aws_cloudwatch_metric_alarm" "changedetection_memory_alarm" {
  alarm_name          = "changedetection-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors ecs memory utilization"
  alarm_actions       = []
  ok_actions          = []

  dimensions = {
    ClusterName = aws_ecs_cluster.changedetection_cluster.name
    ServiceName = aws_ecs_service.changedetection_service.name
  }

  tags = {
    Name = "changedetection-memory-alarm"
  }
}