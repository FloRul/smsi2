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
    
    # Create mount point for the detachable disk
    mkdir -p /mnt/data-disk
    
    # Format disk if needed (only for first time)
    if [ "$(blkid -o value -s TYPE /dev/xvdf || echo '')" = "" ]; then
      mkfs.ext4 /dev/xvdf
    fi
    
    # Add disk to fstab for auto-mounting on reboot
    echo "/dev/xvdf /mnt/data-disk ext4 defaults,nofail 0 2" >> /etc/fstab
    
    # Mount the disk
    mount /mnt/data-disk || echo "Disk mount failed, will try again later"
    
    # Create the directory structure on the detachable disk
    mkdir -p /mnt/data-disk/changedetection/datastore
    
    # Create a symlink for easier access
    ln -sf /mnt/data-disk/changedetection /opt/changedetection
    
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
          - /mnt/data-disk/changedetection/datastore:/datastore
        environment:
          - PUID=1000
          - PGID=1000
          - PLAYWRIGHT=true
    DOCKERCOMPOSE
    
    cd /opt/changedetection
    docker-compose up -d
  EOF
}

# Create a Lightsail disk
resource "aws_lightsail_disk" "changedetection_data" {
  name              = "changedetection-data"
  size_in_gb        = var.disk_size_gb
  availability_zone = "${var.aws_region}a"
  tags = {
    Name = "changedetection-data"
  }
}

# Attach the disk to the instance
resource "aws_lightsail_disk_attachment" "changedetection_disk_attachment" {
  disk_name     = aws_lightsail_disk.changedetection_data.name
  instance_name = aws_lightsail_instance.changedetection.name
  disk_path     = "/dev/xvdf"
}

resource "aws_lightsail_instance_public_ports" "changedetection_ports" {
  instance_name = aws_lightsail_instance.changedetection.name

  port_info {
    protocol  = "tcp"
    from_port = 22
    to_port   = 22
    cidrs     = var.whitelist_ips
  }

  port_info {
    protocol  = "tcp"
    from_port = 5000
    to_port   = 5000
    cidrs     = var.whitelist_ips
  }
}