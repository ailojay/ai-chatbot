provider "aws" {
  region = "us-east-1"
}

# ---------------------------
# DynamoDB (chat sessions)
# ---------------------------
resource "aws_dynamodb_table" "chat_sessions" {
  name         = "chat-sessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }
}

# ---------------------------
# IAM Role for Lambda
# ---------------------------
resource "aws_iam_role" "lambda_role" {
  name = "chatbot-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Basic logging
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DynamoDB access (scoped)
resource "aws_iam_role_policy" "dynamodb_access" {
  name = "dynamodb-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:Scan"
      ]
      Resource = aws_dynamodb_table.chat_sessions.arn
    }]
  })
}

# ---------------------------
# CloudWatch Logs
# ---------------------------
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/ai-chatbot"
  retention_in_days = 7
}

# ---------------------------
# Lambda Function
# ---------------------------
resource "aws_lambda_function" "chatbot" {
  function_name = "ai-chatbot"

  runtime = "python3.12"
  handler = "handler.lambda_handler"

  role = aws_iam_role.lambda_role.arn

  filename         = "../../lambda.zip"
  source_code_hash = filebase64sha256("../../lambda.zip")

  timeout = 10

  environment {
    variables = {
      GEMINI_API_KEY = var.gemini_api_key
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda
  ]
}

# ---------------------------
# API Gateway (HTTP API)
# ---------------------------
resource "aws_apigatewayv2_api" "api" {
  name          = "chatbot-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id           = aws_apigatewayv2_api.api.id
  integration_type = "AWS_PROXY"

  integration_uri = aws_lambda_function.chatbot.invoke_arn
}

resource "aws_apigatewayv2_route" "chat" {
  api_id    = aws_apigatewayv2_api.api.id
  route_key = "POST /chat"

  target = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.api.id
  name        = "$default"
  auto_deploy = true
}

# ---------------------------
# Lambda Permission for API Gateway
# ---------------------------
resource "aws_lambda_permission" "api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.chatbot.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.api.execution_arn}/*/*"
}
