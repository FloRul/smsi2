provider "aws" {
  region = var.aws_region
}

resource "aws_lightsail_instance" "changedetection" {
  name              = "changedetection-instance"
  availability_zone = "${var.aws_region}a"
  blueprint_id      = "ubuntu_20_04"
  bundle_id         = "nano_2_0"
  tags = {
    Name = "changedetection-instance"
  }

  user_data = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose
    systemctl enable docker
    systemctl start docker
    
    mkdir -p /opt/changedetection/datastore
    
    cat > /opt/changedetection/docker-compose.yml << 'DOCKERCOMPOSE'
    version: '3'
    services:
      changedetection:
        image: dgtlmoon/changedetection.io
        container_name: changedetection
        hostname: changedetection
        restart: unless-stopped
        ports:
          - 5000:5000
        volumes:
          - /opt/changedetection/datastore:/datastore
        environment:
          - PUID=1000
          - PGID=1000
          - PLAYWRIGHT=true
    DOCKERCOMPOSE
    
    cd /opt/changedetection
    docker-compose up -d
  EOF
}

resource "aws_lightsail_instance_public_ports" "changedetection_ports" {
  instance_name = aws_lightsail_instance.changedetection.name

  port_info {
    protocol  = "tcp"
    from_port = 22
    to_port   = 22
    cidrs     = [var.whitelist_ip]
  }

  port_info {
    protocol  = "tcp"
    from_port = 5000
    to_port   = 5000
    cidrs     = [var.whitelist_ip]
  }
}