resource "aws_security_group" "changedetection_lb_sg" {
  name        = "changedetection-lb-sg"
  description = "Security group for ChangeDetection load balancer"
  vpc_id      = aws_vpc.changedetection_vpc.id

  # Only allow inbound HTTP traffic from whitelisted IPs
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.whitelist_ips
    description = "HTTP from whitelisted IPs"
  }

  # Only allow inbound HTTPS traffic from whitelisted IPs
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.whitelist_ips
    description = "HTTPS from whitelisted IPs"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "changedetection-lb-sg"
  }
}

resource "aws_security_group" "changedetection_ecs_sg" {
  name        = "changedetection-ecs-sg"
  description = "Security group for ChangeDetection ECS tasks"
  vpc_id      = aws_vpc.changedetection_vpc.id

  # Allow inbound access only from the load balancer
  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.changedetection_lb_sg.id]
    description     = "Access from load balancer"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "changedetection-ecs-sg"
  }
}

resource "aws_security_group" "changedetection_efs_sg" {
  name        = "changedetection-efs-sg"
  description = "Security group for ChangeDetection EFS file system"
  vpc_id      = aws_vpc.changedetection_vpc.id

  # Allow NFS access from the ECS tasks
  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.changedetection_ecs_sg.id]
    description     = "NFS from ECS tasks"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "changedetection-efs-sg"
  }
}