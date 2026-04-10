variable "gemini_api_key" {
  description = "Gemini API Key"
  type        = string
}

data "aws_ssm_parameter" "telegram_token" {
  name            = "/chatbot/telegram/token"
  with_decryption = true
}

data "aws_ssm_parameter" "admin_token" {
  name            = "/chatbot/admin/token"
  with_decryption = true
}
