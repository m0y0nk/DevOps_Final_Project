# LabTrack AWS Infrastructure (Terraform)

This directory provisions the AWS infrastructure for LabTrack using Terraform in accordance with Module **M7** of the grading rubric.

## Architecture

- **Dedicated VPC**: 10.0.0.0/16
- **Subnets**: 2 Public Subnets distributed across distinct Availability Zones in `ap-south-1`
- **Internet Gateway & Route Tables**: Configured with automatic public route associations
- **EKS Control Plane**: Managed Kubernetes cluster (v1.30)
- **EKS Managed Node Group**: EC2 worker nodes (`t3.medium`, 2 desired, min 1, max 3)
- **IAM Roles & Policies**: Dedicated roles for EKS cluster control plane and worker nodes

---

## Cost Warning & Teardown Guardrails

> [!CAUTION]
> Provisioning an EKS cluster ($0.10/hour), worker nodes (EC2 compute), and related AWS networking incurs real cloud costs.
> Always run `terraform destroy` when you finish grading or testing.

---

## Prerequisites

1. Install [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).
2. Configure credentials with sufficient IAM permissions:
   ```bash
   aws configure
   ```
3. Install [Terraform v1.5+](https://developer.hashicorp.com/terraform/downloads).

---

## Usage Instructions

### 1. Initialize Terraform
```bash
cd terraform
terraform init
```

### 2. Format & Validate
```bash
terraform fmt -check
terraform validate
```

### 3. Review Execution Plan
```bash
terraform plan
```
*(Take a screenshot of the plan output for your M7 submission).*

### 4. Apply (Provisions Real AWS Resources)
```bash
terraform apply
```
*(Wait ~12-15 minutes for EKS cluster and node group provisioning).*

### 5. Configure Kubectl
```bash
aws eks update-kubeconfig --region ap-south-1 --name labtrack-eks
kubectl get nodes
```

### 6. Teardown / Cleanup
```bash
terraform destroy
```
*(Confirm destruction to ensure zero unexpected cloud charges).*
