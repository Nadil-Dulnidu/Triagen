# 1. FastAPI Backend API Service
resource "google_cloud_run_v2_service" "api" {
  name     = "${var.project_name}-${var.environment}-api"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = var.backend_sa_email

    scaling {
      min_instance_count = var.api_min_instances
      max_instance_count = var.api_max_instances
    }

    vpc_access {
      connector = var.vpc_connector_id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    containers {
      image = var.api_image

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      ports {
        container_port = 8000
      }

      env {
        name  = "APP_ENV"
        value = var.environment
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_REGION"
        value = var.region
      }
      env {
        name  = "DATABASE_URL"
        value = var.database_url
      }
      env {
        name  = "REDIS_URL"
        value = var.redis_url
      }
      env {
        name  = "CELERY_BROKER_URL"
        value = var.redis_url
      }
      env {
        name  = "CELERY_RESULT_BACKEND"
        value = var.redis_url
      }
      env {
        name  = "GITHUB_APP_ID"
        value = var.github_app_id
      }

      # Secrets mounted from Secret Manager
      env {
        name = "GITHUB_APP_PRIVATE_KEY"
        value_source {
          secret_key_ref {
            secret  = var.secret_names["github_app_private_key"]
            version = "latest"
          }
        }
      }
      env {
        name = "GITHUB_WEBHOOK_SECRET"
        value_source {
          secret_key_ref {
            secret  = var.secret_names["github_webhook_secret"]
            version = "latest"
          }
        }
      }
      env {
        name = "CLERK_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = var.secret_names["clerk_secret_key"]
            version = "latest"
          }
        }
      }
      env {
        name = "CLERK_WEBHOOK_SIGNING_SECRET"
        value_source {
          secret_key_ref {
            secret  = var.secret_names["clerk_webhook_signing_secret"]
            version = "latest"
          }
        }
      }
      env {
        name = "PINECONE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = var.secret_names["pinecone_api_key"]
            version = "latest"
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        period_seconds    = 15
        failure_threshold = 3
      }
    }
  }
}

# Allow public invocations for FastAPI API
resource "google_cloud_run_service_iam_member" "api_public" {
  service  = google_cloud_run_v2_service.api.name
  location = var.region
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 2. Celery Review Worker Service
resource "google_cloud_run_v2_service" "worker" {
  name     = "${var.project_name}-${var.environment}-worker"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    service_account = var.backend_sa_email

    scaling {
      min_instance_count = var.worker_min_instances
      max_instance_count = var.worker_max_instances
    }

    vpc_access {
      connector = var.vpc_connector_id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    containers {
      image   = var.api_image
      command = ["celery", "-A", "server.workers.celery_app", "worker", "--loglevel=INFO", "-c", "4"]

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }

      env {
        name  = "APP_ENV"
        value = var.environment
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_REGION"
        value = var.region
      }
      env {
        name  = "DATABASE_URL"
        value = var.database_url
      }
      env {
        name  = "REDIS_URL"
        value = var.redis_url
      }
      env {
        name  = "CELERY_BROKER_URL"
        value = var.redis_url
      }
      env {
        name  = "CELERY_RESULT_BACKEND"
        value = var.redis_url
      }
      env {
        name  = "GITHUB_APP_ID"
        value = var.github_app_id
      }

      env {
        name = "GITHUB_APP_PRIVATE_KEY"
        value_source {
          secret_key_ref {
            secret  = var.secret_names["github_app_private_key"]
            version = "latest"
          }
        }
      }
      env {
        name = "PINECONE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = var.secret_names["pinecone_api_key"]
            version = "latest"
          }
        }
      }
    }
  }
}

# 3. Next.js 15 Frontend Client Service
resource "google_cloud_run_v2_service" "client" {
  name     = "${var.project_name}-${var.environment}-client"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = var.frontend_sa_email

    scaling {
      min_instance_count = var.client_min_instances
      max_instance_count = var.client_max_instances
    }

    containers {
      image = var.client_image

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }

      ports {
        container_port = 3000
      }

      env {
        name  = "NODE_ENV"
        value = "production"
      }
      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.api.uri
      }
      env {
        name  = "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"
        value = var.clerk_publishable_key
      }
      env {
        name = "CLERK_SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = var.secret_names["clerk_secret_key"]
            version = "latest"
          }
        }
      }
    }
  }
}

# Allow public invocations for Next.js Client
resource "google_cloud_run_service_iam_member" "client_public" {
  service  = google_cloud_run_v2_service.client.name
  location = var.region
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}
