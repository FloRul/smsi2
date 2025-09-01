# ChangeDetection.io on AWS

This repository contains Terraform configuration to deploy [ChangeDetection.io](https://github.com/dgtlmoon/changedetection.io) on AWS using GitHub Actions.

## Prerequisites

1. AWS account with sufficient permissions
2. GitHub repository secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `WHITELIST_IP`: Your IP addresses to whitelist in CIDR notation (e.g., ["123.123.123.123/32", "..."])

## How it Works

- The GitHub Actions workflow in `.github/workflows/terraform-deploy.yml` runs when you push to the main branch or manually trigger it.
- Terraform deploys a Fargate tasks and a load balancer
- Only the specified IP address in `WHITELIST_IP` can reach the loadbalancer

## Deployment

1. Fork or clone this repository
2. Add the required secrets to your GitHub repository settings
3. Push to the main branch or manually trigger the workflow

After deployment, you can access ChangeDetection.io at the "http://${aws_lb.changedetection_lb.dns_name}"

## Local Development

To run Terraform locally:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```