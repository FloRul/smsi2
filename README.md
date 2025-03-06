# ChangeDetection.io on AWS Lightsail

This repository contains Terraform configuration to deploy [ChangeDetection.io](https://github.com/dgtlmoon/changedetection.io) on AWS Lightsail using GitHub Actions.

## Prerequisites

1. AWS account with sufficient permissions
2. GitHub repository secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `WHITELIST_IP`: Your IP address in CIDR notation (e.g., 123.123.123.123/32)

## How it Works

- The GitHub Actions workflow in `.github/workflows/terraform-deploy.yml` runs when you push to the main branch or manually trigger it.
- Terraform creates an AWS Lightsail instance with Ubuntu 20.04, installs Docker, and deploys ChangeDetection.io.
- Only the specified IP address in `WHITELIST_IP` can access the instance via SSH (port 22) and the ChangeDetection.io web interface (port 5000).

## Deployment

1. Fork or clone this repository
2. Add the required secrets to your GitHub repository settings
3. Push to the main branch or manually trigger the workflow

After deployment, you can access ChangeDetection.io at: `http://<instance_ip>:5000`

## Local Development

To run Terraform locally:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Customization

- Edit `variables.tf` to change the AWS region (default: us-east-1)
- Modify `main.tf` to change the Lightsail instance size or configuration