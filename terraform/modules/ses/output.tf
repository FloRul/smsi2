output "notification_ses_identity" {
  value = data.aws_ses_email_identity.notification.email
}
