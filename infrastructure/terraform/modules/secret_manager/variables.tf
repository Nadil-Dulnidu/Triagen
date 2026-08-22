variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "project_name" {
  description = "Application project prefix"
  type        = string
  default     = "triagen"
}

variable "environment" {
  description = "Deployment environment (staging/production)"
  type        = string
}

variable "github_app_private_key" {
  description = "GitHub App RS256 Private Key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "github_webhook_secret" {
  description = "GitHub App Webhook HMAC Secret"
  type        = string
  default     = ""
  sensitive   = true
}

variable "clerk_secret_key" {
  description = "Clerk Backend Secret Key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "clerk_webhook_signing_secret" {
  description = "Clerk Svix Webhook Secret"
  type        = string
  default     = ""
  sensitive   = true
}

variable "pinecone_api_key" {
  description = "Pinecone Vector DB API Key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "database_url" {
  description = "Database connection string"
  type        = string
  default     = ""
  sensitive   = true
}
