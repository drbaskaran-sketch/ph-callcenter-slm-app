# =====================================================================
# PRASHANTH HOSPITALS — TERRAFORM AWS VPS PROVISIONING MANIFEST
# =====================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "ap-south-1" # AWS Mumbai Region
}

variable "instance_type" {
  default = "t3.medium"
}

# 1. AWS Security Group Firewall Definition
resource "aws_security_group" "ph_slm_sg" {
  name        = "ph-slm-security-group"
  description = "Strict Firewall Rules for Prashanth Hospitals SLM App"

  # Ingress Rule 1: SSH (Port 22)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH Key-Based Access"
  }

  # Ingress Rule 2: HTTP (Port 80)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP Traffic"
  }

  # Ingress Rule 3: HTTPS (Port 443)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS Secure Traffic"
  }

  # Ingress Rule 4: Vite React Frontend (Port 5173)
  ingress {
    from_port   = 5173
    to_port     = 5173
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Vite React Frontend"
  }

  # Ingress Rule 5: FastAPI Backend (Port 8000)
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "FastAPI Backend API"
  }

  # Egress Rule: Allow All Outbound Traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "ph-slm-security-group"
    Environment = "Production"
  }
}

# 2. AWS EC2 Cloud VPS Instance Provisioning
resource "aws_instance" "ph_slm_vps" {
  ami           = "ami-00bb6a80f01f03502" # Ubuntu 24.04 LTS LTS
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.ph_slm_sg.id]
  key_name               = "ph-ec2-key"

  root_block_device {
    volume_size = 30 # 30 GB SSD
    volume_type = "gp3"
  }

  user_data = <<-EOF
              #!/bin/bash
              echo "Executing server provisioning & security hardening..."
              curl -sSL https://raw.githubusercontent.com/drbaskaran-sketch/ph-callcenter-slm-app/main/scripts/provision_server_security.sh | bash
              EOF

  tags = {
    Name        = "ph-slm-production-vps"
    Environment = "Production"
  }
}

output "instance_public_ip" {
  value       = aws_instance.ph_slm_vps.public_ip
  description = "Public IP Address of Provisioned Cloud VPS"
}
