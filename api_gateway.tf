resource "aws_api_gateway_rest_api" "dns-manager" {
  name                     = "dns-manager"
  description              = "API for dns-manager lambda function"
  api_key_source           = "HEADER"
  binary_media_types       = []
  minimum_compression_size = -1
  tags                     = {}

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_method" "post" {
  resource_id          = aws_api_gateway_rest_api.dns-manager.root_resource_id
  rest_api_id          = aws_api_gateway_rest_api.dns-manager.id
  api_key_required     = false
  authorization        = "NONE"
  authorization_scopes = []
  http_method          = "POST"
  request_models       = {}
  request_parameters   = {}
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.dns-manager.id
  resource_id = aws_api_gateway_rest_api.dns-manager.root_resource_id
  http_method = aws_api_gateway_method.post.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  response_parameters = {}
}

resource "aws_api_gateway_integration" "dns-manager" {
  resource_id             = aws_api_gateway_rest_api.dns-manager.root_resource_id
  rest_api_id             = aws_api_gateway_rest_api.dns-manager.id
  cache_key_parameters    = []
  connection_type         = "INTERNET"
  content_handling        = "CONVERT_TO_TEXT"
  http_method             = "POST"
  integration_http_method = "POST"
  passthrough_behavior    = "WHEN_NO_MATCH"
  request_parameters      = {}
  request_templates       = {}
  timeout_milliseconds    = 29000
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.dns-manager.invoke_arn
}

resource "aws_api_gateway_deployment" "dns-manager" {
  depends_on = [aws_api_gateway_integration.dns-manager]

  rest_api_id = aws_api_gateway_rest_api.dns-manager.id
  stage_name  = "prod"
}
