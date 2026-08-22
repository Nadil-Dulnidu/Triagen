locals {
  secrets = {
    "github_app_private_key"       = var.github_app_private_key
    "github_webhook_secret"        = var.github_webhook_secret
    "clerk_secret_key"             = var.clerk_secret_key
    "clerk_webhook_signing_secret" = var.clerk_webhook_signing_secret
    "pinecone_api_key"             = var.pinecone_api_key
    "database_url"                 = var.database_url
  }
}

resource "google_secret_manager_secret" "secret" {
  for_each  = local.secrets
  secret_id = "${var.project_name}-${var.environment}-${replace(each.key, "_", "-")}"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "secret_version" {
  for_each    = { for k, v in local.secrets : k => v if v != "" }
  secret      = google_secret_manager_secret.secret[each.key].id
  secret_data = each.value
}
