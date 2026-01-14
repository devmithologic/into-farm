# My First Terraform Lab

A hands-on beginner's guide to Infrastructure as Code (IaC) using Terraform and AWS.

## What You'll Learn

- What problem Terraform solves
- Core Terraform concepts (Provider, Resource, Variable, Output, State)
- The Terraform workflow: `init → plan → apply → destroy`
- Creating real AWS infrastructure from code

## Prerequisites

- AWS account with IAM permissions
- AWS CLI installed and configured
- Terraform installed

### Installing Terraform on Ubuntu/WSL

```bash
wget https://releases.hashicorp.com/terraform/1.7.5/terraform_1.7.5_linux_amd64.zip
unzip terraform_1.7.5_linux_amd64.zip
sudo mv terraform /usr/local/bin/
terraform --version
```

### Verify AWS CLI

```bash
aws sts get-caller-identity
```

## Core Concepts

### What Problem Does Terraform Solve?

Imagine managing 50 EC2 instances with their security groups, all connected to an RDS database. Would you create them manually in the AWS console?

**Terraform lets you define infrastructure as code.** You write what you want, and Terraform creates, modifies, or destroys it.

### The 5 Key Concepts

| Concept | Purpose | Example |
|---------|---------|---------|
| **Provider** | Connects Terraform to a cloud service | `provider "aws" { region = "us-east-1" }` |
| **Resource** | The infrastructure you want to create | `resource "aws_instance" "server" { ... }` |
| **Variable** | Reusable parameters | `variable "environment" { default = "dev" }` |
| **Output** | Values returned after creation (IP, DNS, IDs) | `output "public_ip" { value = aws_instance.server.public_ip }` |
| **State** | File that tracks what infrastructure exists | `terraform.tfstate` |

### Why State Matters

The `terraform.tfstate` file is Terraform's source of truth. Without it, Terraform doesn't know what resources already exist and could create duplicates or lose track of infrastructure.

**In teams, state is stored in a remote backend (like S3) so everyone works against the same source of truth.**

## The Terraform Workflow

```
terraform init      # Download providers, initialize directory
terraform plan      # Dry-run: shows what WILL happen (no changes made)
terraform apply     # Execute changes (creates/modifies/destroys resources)
terraform destroy   # Delete all managed resources
```

## Hands-On: Create an EC2 Instance

### Step 1: Find a Valid AMI

AMIs are region-specific. Find an Amazon Linux 2023 AMI for your region:

```bash
aws ec2 describe-images \
  --region us-east-1 \
  --owners amazon \
  --filters "Name=name,Values=al2023-ami-2023*-x86_64" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text
```

### Step 2: Create main.tf

```hcl
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "my_first_server" {
  ami           = "ami-XXXXXXXXX"  # Replace with AMI from Step 1
  instance_type = "t2.micro"

  tags = {
    Name = "terraform-lab"
  }
}

output "public_ip" {
  value = aws_instance.my_first_server.public_ip
}
```

### Step 3: Initialize

```bash
terraform init
```

This downloads the AWS provider and creates:
- `.terraform/` - Provider binaries (don't commit)
- `.terraform.lock.hcl` - Locks provider versions (do commit)

### Step 4: Plan

```bash
terraform plan
```

Review the output. The `+` symbol means "create". You'll see:
- `(known after apply)` - Values AWS assigns at creation time
- `Plan: 1 to add, 0 to change, 0 to destroy` - Summary of changes

### Step 5: Apply

```bash
terraform apply
```

Type `yes` to confirm. Terraform creates the EC2 instance and outputs the public IP.

### Step 6: Verify

Check the AWS Console → EC2 → Instances. Your instance should be running.

### Step 7: Clean Up

```bash
terraform destroy
```

**Always destroy resources when done practicing to avoid charges.**

## Reading terraform plan Output

| Symbol | Meaning |
|--------|---------|
| `+` | Create |
| `~` | Modify |
| `-` | Destroy |

## .gitignore for Terraform

```gitignore
.terraform/
*.tfstate
*.tfstate.backup
*.tfvars
```

> **Note:** State files contain sensitive information. Never commit them to version control. In production, use remote state backends.

## Common Interview Questions

**Q: What is Terraform and why use it?**

A: Terraform is an Infrastructure as Code tool that lets you define, provision, and manage cloud resources using declarative configuration files. It provides version control for infrastructure, enables reproducible environments, and allows infrastructure changes to be reviewed before applying.

**Q: What is the Terraform state and why is it critical?**

A: The state file is Terraform's source of truth about existing infrastructure. It maps configuration to real resources, tracks metadata, and enables Terraform to determine what changes are needed. Without state, Terraform can't manage existing resources. In teams, remote state (S3, Terraform Cloud) ensures everyone works against the same truth.

**Q: What's the difference between `terraform plan` and `terraform apply`?**

A: `plan` is a dry-run that shows what changes Terraform will make without executing them. `apply` actually creates, modifies, or destroys resources. Always run `plan` first to review changes before applying.

## Next Steps

- [ ] Add variables to make the configuration reusable
- [ ] Use remote state with S3 backend
- [ ] Create multiple resources (VPC, Security Groups, EC2)
- [ ] Explore Terraform modules

## Resources

- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://developer.hashicorp.com/terraform/cloud-docs/recommended-practices)