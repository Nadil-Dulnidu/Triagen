output "api_uri" {
  description = "FastAPI Backend Cloud Run URI"
  value       = google_cloud_run_v2_service.api.uri
}

output "worker_name" {
  description = "Celery Worker Cloud Run Name"
  value       = google_cloud_run_v2_service.worker.name
}

output "client_uri" {
  description = "Next.js Frontend Cloud Run URI"
  value       = google_cloud_run_v2_service.client.uri
}
