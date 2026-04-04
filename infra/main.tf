terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "ailojay-chatbot-tfstate"
    key            = "ai-chatbot/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "chatbot-tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

# Get latest Ubuntu 22.04 AMI for your region
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Key pair for SSH access
resource "aws_key_pair" "chatbot_key" {
  key_name   = "${var.app_name}-key"
  public_key = file("~/.ssh/chatbot-key.pub")
}

# Security group
resource "aws_security_group" "chatbot_sg" {
  name        = "${var.app_name}-sg"
  description = "Security group for AI chatbot"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-sg"
  }
}

# EC2 instance
resource "aws_instance" "chatbot" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.chatbot_key.key_name
  vpc_security_group_ids = [aws_security_group.chatbot_sg.id]

  user_data = templatefile("${path.module}/user_data.sh", {
    gemini_api_key = var.gemini_api_key
    github_repo    = var.github_repo
  })

  tags = {
    Name = var.app_name
  }
}

# Elastic IP so address never changes
resource "aws_eip" "chatbot_eip" {
  instance = aws_instance.chatbot.id
  domain   = "vpc"

  tags = {
    Name = "${var.app_name}-eip"
  }
}