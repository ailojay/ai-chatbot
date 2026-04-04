variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "app_name" {
  description = "Application name used for tagging"
  type        = string
  default     = "ai-chatbot"
}

variable "gemini_api_key" {
  description = "Gemini API key - passed at apply time, never stored in code"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "Your GitHub repo URL"
  type        = string
  default     = "https://github.com/ailojay/ai-chatbot.git"
}