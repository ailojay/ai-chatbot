output "public_ip" {
  description = "Public IP address of your chatbot"
  value       = aws_eip.chatbot_eip.public_ip
}

output "public_url" {
  description = "URL to access your chatbot"
  value       = "http://${aws_eip.chatbot_eip.public_ip}"
}

output "ssh_command" {
  description = "Command to SSH into your instance"
  value       = "ssh -i ~/.ssh/chatbot-key.pem ubuntu@${aws_eip.chatbot_eip.public_ip}"
}