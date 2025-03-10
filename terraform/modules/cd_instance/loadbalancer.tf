resource "aws_lb" "changedetection_lb" {
  name               = "changedetection-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.changedetection_lb_sg.id]
  subnets            = [aws_subnet.changedetection_subnet_a.id, aws_subnet.changedetection_subnet_b.id]

  enable_deletion_protection = false

  tags = {
    Name = "changedetection-lb"
  }
}

resource "aws_lb_target_group" "changedetection_tg" {
  name        = "changedetection-tg"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.changedetection_vpc.id
  target_type = "ip"

  health_check {
    enabled             = true
    interval            = 30
    path                = "/api/v1/systeminfo"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    protocol            = "HTTP"
    matcher             = "200-299"
  }

  tags = {
    Name = "changedetection-tg"
  }
}

resource "aws_lb_listener" "changedetection_http" {
  load_balancer_arn = aws_lb.changedetection_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.changedetection_tg.arn
  }

  tags = {
    Name = "changedetection-http-listener"
  }
}

# Future HTTPS support - Commented out for now
/*
resource "aws_acm_certificate" "changedetection_cert" {
  domain_name       = "changedetection.example.com"
  validation_method = "DNS"

  tags = {
    Name = "changedetection-cert"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_listener" "changedetection_https" {
  load_balancer_arn = aws_lb.changedetection_lb.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.changedetection_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.changedetection_tg.arn
  }

  tags = {
    Name = "changedetection-https-listener"
  }
}
*/