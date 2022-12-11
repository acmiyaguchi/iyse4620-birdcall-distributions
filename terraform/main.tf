terraform {
  backend "gcs" {
    bucket = "acmiyaguchi-terraform"
    prefix = "acmiyaguchi/iyse6420-birdcall-distribution"
  }
}

terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
  required_version = ">= 0.13"
}

provider "google" {
  project = "acmiyaguchi"
  region  = "us-central1"
}

resource "google_storage_bucket" "default" {
  name                        = "iyse6420-birdcall-distribution"
  location                    = "US"
  uniform_bucket_level_access = true
  cors {
    origin          = ["*"]
    method          = ["GET"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

// public read access to the bucket
resource "google_storage_bucket_iam_member" "public_read" {
  bucket = google_storage_bucket.default.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
