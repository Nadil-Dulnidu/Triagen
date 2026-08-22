variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "Triagen"
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "prod"
}

variable "region" {
  description = "Default GCP Region"
  type        = string
  default     = "us-central1"
}

variable "github_repo" {
  description = "GitHub repository for Workload Identity"
  type        = string
  default     = "Nadil-Dulnidu/Triagen"
}

variable "github_app_id" {
  description = "GitHub App ID"
  type        = string
}

variable "github_app_private_key" {
  description = "GitHub App Private Key (PEM)"
  type        = string
  sensitive   = true
}

variable "github_webhook_secret" {
  description = "GitHub Webhook Secret"
  type        = string
  sensitive   = true
}

variable "clerk_publishable_key" {
  description = "Clerk Frontend Publishable Key"
  type        = string
}

variable "clerk_secret_key" {
  description = "Clerk Backend Secret Key"
  type        = string
  sensitive   = true
}

variable "clerk_webhook_signing_secret" {
  description = "Clerk Svix Webhook Signing Secret"
  type        = string
  sensitive   = true
}

variable "pinecone_api_key" {
  description = "Pinecone API Key"
  type        = string
  sensitive   = true
}

variable "db_tier" {
  description = "Cloud SQL machine tier (e.g. db-custom-2-7680 or db-f1-micro)"
  type        = string
  default     = "db-custom-2-7680"
}

variable "deletion_protection" {
  description = "Prevent accidental destruction of DB instance"
  type        = bool
  default     = false
}

variable "api_min_instances" {
  description = "Minimum API instances (0 allows scaling to zero when idle to save cost)"
  type        = number
  default     = 0
}

variable "api_image" {
  description = "Initial Docker image for API/Worker"
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "client_image" {
  description = "Initial Docker image for Next.js Client"
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}
