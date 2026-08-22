provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# 1. VPC & Networking
module "vpc" {
  source       = "./modules/vpc"
  project_id   = var.project_id
  project_name = var.project_name
  environment  = var.environment
  region       = var.region
  subnet_cidr  = "10.0.0.0/20"
  connector_cidr = "10.8.0.0/28"
}

# 2. Cloud SQL PostgreSQL 16
module "cloud_sql" {
  source              = "./modules/cloud_sql"
  project_id          = var.project_id
  project_name        = var.project_name
  environment         = var.environment
  region              = var.region
  network_id          = module.vpc.network_id
  psa_connection      = module.vpc.network_id
  tier                = var.db_tier
  availability_type   = "ZONAL"
  disk_size           = 20
  deletion_protection = var.deletion_protection
}

# 3. Memorystore Redis 7
module "memorystore" {
  source         = "./modules/memorystore"
  project_id     = var.project_id
  project_name   = var.project_name
  environment    = var.environment
  region         = var.region
  network_id     = module.vpc.network_id
  psa_connection = module.vpc.network_id
  tier           = "BASIC"
  memory_size_gb = 1
}

# 4. Artifact Registry
module "artifact_registry" {
  source       = "./modules/artifact_registry"
  project_id   = var.project_id
  project_name = var.project_name
  environment  = var.environment
  region       = var.region
}

# 5. Secret Manager
module "secret_manager" {
  source                       = "./modules/secret_manager"
  project_id                   = var.project_id
  project_name                 = var.project_name
  environment                  = var.environment
  github_app_private_key       = var.github_app_private_key
  github_webhook_secret        = var.github_webhook_secret
  clerk_secret_key             = var.clerk_secret_key
  clerk_webhook_signing_secret = var.clerk_webhook_signing_secret
  pinecone_api_key             = var.pinecone_api_key
  database_url                 = module.cloud_sql.database_url
}

# 6. IAM & Workload Identity
module "iam" {
  source                   = "./modules/iam"
  project_id               = var.project_id
  project_name             = var.project_name
  environment              = var.environment
  enable_workload_identity = true
  github_repo              = var.github_repo
}

# 7. Cloud Run Services
module "cloud_run" {
  source                = "./modules/cloud_run"
  project_id            = var.project_id
  project_name          = var.project_name
  environment           = var.environment
  region                = var.region
  backend_sa_email      = module.iam.backend_sa_email
  frontend_sa_email     = module.iam.frontend_sa_email
  vpc_connector_id      = module.vpc.connector_id
  api_image             = var.api_image
  client_image          = var.client_image
  database_url          = module.cloud_sql.database_url
  redis_url             = module.memorystore.redis_url
  github_app_id         = var.github_app_id
  clerk_publishable_key = var.clerk_publishable_key
  secret_names          = module.secret_manager.secret_names
  api_min_instances     = var.api_min_instances
  worker_min_instances  = 1
  client_min_instances  = 0
}
