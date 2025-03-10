resource "aws_vpc" "changedetection_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "changedetection-vpc"
  }
}

resource "aws_subnet" "changedetection_subnet_a" {
  vpc_id                  = aws_vpc.changedetection_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "changedetection-subnet-a"
  }
}

resource "aws_subnet" "changedetection_subnet_b" {
  vpc_id                  = aws_vpc.changedetection_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "changedetection-subnet-b"
  }
}

resource "aws_internet_gateway" "changedetection_igw" {
  vpc_id = aws_vpc.changedetection_vpc.id

  tags = {
    Name = "changedetection-igw"
  }
}

resource "aws_route_table" "changedetection_rt" {
  vpc_id = aws_vpc.changedetection_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.changedetection_igw.id
  }

  tags = {
    Name = "changedetection-rt"
  }
}

resource "aws_route_table_association" "changedetection_rta_a" {
  subnet_id      = aws_subnet.changedetection_subnet_a.id
  route_table_id = aws_route_table.changedetection_rt.id
}

resource "aws_route_table_association" "changedetection_rta_b" {
  subnet_id      = aws_subnet.changedetection_subnet_b.id
  route_table_id = aws_route_table.changedetection_rt.id
}