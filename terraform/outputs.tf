output "cluster_name" {
  description = "The name of the provisioned EKS cluster"
  value       = aws_eks_cluster.main.name
}

output "cluster_endpoint" {
  description = "The endpoint for the Kubernetes API server"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_arn" {
  description = "The ARN of the EKS cluster"
  value       = aws_eks_cluster.main.arn
}

output "vpc_id" {
  description = "The ID of the dedicated LabTrack VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "The IDs of the public subnets created across availability zones"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "configure_kubectl" {
  description = "Command to configure kubectl to point to this EKS cluster"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.main.name}"
}
