resource "aws_iam_role" "dns-manager" {
  name                  = "dns-manager"
  force_detach_policies = true
  assume_role_policy    = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}

EOF

  tags = {
    Creator = "cluster.dev"
  }
}

resource "aws_iam_role_policy" "dns-manager" {
  name = "dns-manager"
  role = aws_iam_role.dns-manager.id

  policy = <<-EOF
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Sid": "VisualEditor0",
              "Effect": "Allow",
              "Action": [
                  "logs:CreateLogStream",
                  "sts:AssumeRole",
                  "route53:*",
                  "dynamodb:*",
                  "logs:CreateLogGroup",
                  "logs:PutLogEvents"
              ],
              "Resource": "*"
          }
      ]
  }
  EOF
}

#resource "aws_iam_role_policy_attachment" "dns-manager" {
#  role       = "${aws_iam_role.dns-manager.name}"
#  policy_arn = "${aws_iam_role_policy.dns-manager.arn}"
#}
