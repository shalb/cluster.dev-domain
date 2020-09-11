resource "aws_lambda_function" "dns-manager" {
  function_name                  = "dns-manager"
  filename                       = "dns-manager.zip"
  source_code_hash               = filebase64sha256("dns-manager.zip")
  handler                        = "lambda_function.lambda_handler"
  role                           = aws_iam_role.dns-manager.arn
  memory_size                    = 128
  publish                        = false
  reserved_concurrent_executions = -1
  runtime                        = "python3.8"
  timeout                        = 3

  environment {
    variables = {
      DYNAMODB_TABLE_NAME = "dns-manager"
      LOG_LEVEL           = "DEBUG"
    }
  }

  tags = {
    Creator = "cluster.dev"
  }

  tracing_config {
    mode = "PassThrough"
  }
}

resource "aws_lambda_permission" "dns-manager" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dns-manager.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.dns-manager.execution_arn}/*/POST/"
}
