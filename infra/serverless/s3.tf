# ============================
# S3 bucket for admin UI
# ============================

resource "aws_s3_bucket" "admin_ui" {
  bucket = "mamatiti-admin-ui"

  website {
    index_document = "admin_login.html"
    error_document = "admin_login.html"
  }

  # Force destroy allows you to terraform destroy without manual cleanup
  force_destroy = true
}

# Allow public read for the static website
resource "aws_s3_bucket_policy" "admin_ui_policy" {
  bucket = aws_s3_bucket.admin_ui.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicRead"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject"]
        Resource  = "${aws_s3_bucket.admin_ui.arn}/*"
      }
    ]
  })
}

# Optional: Block public access settings overridden for website
resource "aws_s3_bucket_public_access_block" "admin_ui_block" {
  bucket = aws_s3_bucket.admin_ui.id

  block_public_acls       = false
  ignore_public_acls      = false
  block_public_policy     = false
  restrict_public_buckets = false
}
