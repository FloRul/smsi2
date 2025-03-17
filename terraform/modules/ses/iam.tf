resource "aws_iam_user" "ses_user" {
  name = "changedetection-ses-smtp-user"
}

resource "aws_iam_access_key" "ses_user_key" {
  user = aws_iam_user.ses_user.name
}

resource "aws_iam_user_policy" "ses_policy" {
  name = "changedetection-ses-send-email-policy"
  user = aws_iam_user.ses_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ses:FromAddress" = data.aws_ses_email_identity.notification.email
          }
        }
      }
    ]
  })
}
