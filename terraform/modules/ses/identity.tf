# Create an SES email identity
data "aws_ses_email_identity" "notification" {
  email = "notification@regulatorytracking.levio.ca"
}
