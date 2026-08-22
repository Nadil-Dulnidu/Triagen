variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "project_name" {
  description = "Application project prefix"
  type        = string
  default     = "pullsense"
}

variable "environment" {
  description = "Deployment environment (staging/production)"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "backend_sa_email" {
  description = "Backend Service Account Email"
  type        = string
}

variable "frontend_sa_email" {
  description = "Frontend Service Account Email"
  type        = string
}

variable "vpc_connector_id" {
  description = "Serverless VPC Access Connector ID"
  type        = string
}

variable "api_image" {
  description = "Docker image URI for FastAPI & Celery services"
  type        = string
}

variable "client_image" {
  description = "Docker image URI for Next.js client"
  type        = string
}

variable "database_url" {
  description = "Cloud SQL asyncpg database connection string"
  type        = string
  sensitive   = true
}

variable "redis_url" {
  description = "Memorystore Redis URL"
  type        = string
}

variable "github_app_id" {
  description = "GitHub App ID"
  type        = string
  default     = "123456"
}

variable "clerk_publishable_key" {
  description = "Clerk Frontend Publishable Key"
  type        = string
  default     = ""
}

variable "secret_names" {
  description = "Map of Secret Manager secret names"
  type        = map(string)
}

variable "api_min_instances" {
  description = "Min API instances (0 for staging scale-to-zero, 1+ for prod)"
  type        = number
  default     = 0
}

variable "api_max_instances" {
  description = "Max API instances"
  type        = number
  default     = 10
}

variable "worker_min_instances" {
  description = "Min worker instances"
  type        = number
  default     = 1
}

variable "worker_max_instances" {
  description = "Max worker instances"
  type        = number
  default     = 5
}

variable "client_min_instances" {
  description = "Min client instances"
  type        = number
  default     = 0
}

variable "client_max_instances" {
  description = "Max client instances"
  type        = number
  default     = 5
}
