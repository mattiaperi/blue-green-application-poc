# https://kreuzwerker.de/post/how-to-leverage-image-vulnerability-scanning-on-aws-ecr-using-a-fully

# ECR Repository with “scan on push” enabled
resource "aws_ecr_repository" "ecr_repo" {
  name = "ecr_repo"
  image_scanning_configuration {
    scan_on_push = true
  }
}

# An AWS Event Bridge rule (formerly Cloudwatch rule, in terraform still Cloudwatch) to receive and handle events
resource "aws_cloudwatch_event_rule" "ecr_scan_event" {
  name          = "ecr_scan_event"
  description   = "Triggered when image scan was completed."
  event_pattern = <<EOF
  {
  "detail-type": ["ECR Image Scan"],
  "source": ["aws.ecr"],
  "detail": {
    "repository-name": [{
      "prefix": "${aws_ecr_repository.ecr_repo.name}"
    }]
  }
}
  EOF
  role_arn = aws_iam_role.ecr_scan_role.arn
}

# AWS Event Bridge rule target: an SNS topic
resource "aws_cloudwatch_event_target" "ecr_scan_event_target" {
  rule = aws_cloudwatch_event_rule.ecr_scan_event.name
  arn  = aws_sns_topic.ecr_scan_sns_topic.arn
  input_transformer {
    input_paths    = { "findings" : "$.detail.finding-severity-counts", "repo" : "$.detail.repository-name", "digest" : "$.detail.image-digest", "time" : "$.time", "status" : "$.detail.scanstatus", "tags" : "$.detail.image-tags", "account" : "$.account", "region" : "$.region" }
    input_template = <<EOF
"ECR Image scan results:"
"Time: <time>"
"Acc : <account>"
"Repo: <repo>"
"SHA : <digest>"
"Tags: <tags>"
"Find: <findings>"
EOF
  }
}

# SNS subscription which forwards to lambda
resource "aws_sns_topic_subscription" "ecr_scan_sns_topic_subscription" {
  topic_arn = aws_sns_topic.ecr_scan_sns_topic.id
  protocol  = "lambda"
  endpoint  = aws_lambda_function.ecr_scan_notification_lambda.arn
}

# The target lambda function
resource "aws_lambda_function" "ecr_scan_notification_lambda" {
  function_name = "ecr_scan_notification_lambda"
  filename      = "${path.module}/slackify.zip"
  role          = aws_iam_role.ecr_scan_notification_lambda_role.arn
  runtime       = "python3.8"
  handler       = "slackify.lambda_handler"
  depends_on = [data.archive_file.slackify-zip]
  environment {
    variables = {
      SLACK_WEBHOOK = var.slack_webhook
    }
  }
}
