resource "aws_ecs_cluster" "changedetection_cluster" {
  name = "changedetection-cluster"

  tags = {
    Name = "changedetection-cluster"
  }
}

resource "aws_cloudwatch_log_group" "changedetection_logs" {
  name              = "/ecs/changedetection"
  retention_in_days = 30

  tags = {
    Name = "changedetection-logs"
  }
}

resource "aws_ecs_task_definition" "changedetection_task" {
  family                   = "changedetection-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "changedetection-container"
      image     = "dgtlmoon/changedetection.io:latest"
      essential = true

      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "WEBDRIVER_URL"
          value = ""
        },
        {
          name  = "BASE_URL"
          value = ""
        }
      ]

      mountPoints = [
        {
          sourceVolume  = "changedetection-data"
          containerPath = "/datastore"
          readOnly      = false
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.changedetection_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  volume {
    name = "changedetection-data"

    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.changedetection_data.id
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.changedetection_access_point.id
        iam             = "ENABLED"
      }
    }
  }

  tags = {
    Name = "changedetection-task-definition"
  }
}

resource "aws_ecs_service" "changedetection_service" {
  name                              = "changedetection-service"
  cluster                           = aws_ecs_cluster.changedetection_cluster.id
  task_definition                   = aws_ecs_task_definition.changedetection_task.arn
  desired_count                     = 1
  launch_type                       = "FARGATE"
  platform_version                  = "LATEST"
  health_check_grace_period_seconds = 60

  network_configuration {
    subnets          = [aws_subnet.changedetection_subnet_a.id, aws_subnet.changedetection_subnet_b.id]
    security_groups  = [aws_security_group.changedetection_ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.changedetection_tg.arn
    container_name   = "changedetection-container"
    container_port   = 5000
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  depends_on = [
    aws_lb.changedetection_lb,
    aws_iam_role_policy_attachment.ecs_execution_role_policy
  ]

  tags = {
    Name = "changedetection-service"
  }
}
