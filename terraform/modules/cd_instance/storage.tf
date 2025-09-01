resource "aws_efs_file_system" "changedetection_data" {
  creation_token   = "changedetection-data"
  performance_mode = "generalPurpose"
  throughput_mode  = "bursting"
  encrypted        = true

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  tags = {
    Name = "changedetection-data"
  }
}

resource "aws_efs_mount_target" "changedetection_mount_a" {
  file_system_id  = aws_efs_file_system.changedetection_data.id
  subnet_id       = aws_subnet.changedetection_subnet_a.id
  security_groups = [aws_security_group.changedetection_efs_sg.id]
}

resource "aws_efs_mount_target" "changedetection_mount_b" {
  file_system_id  = aws_efs_file_system.changedetection_data.id
  subnet_id       = aws_subnet.changedetection_subnet_b.id
  security_groups = [aws_security_group.changedetection_efs_sg.id]
}

resource "aws_efs_access_point" "changedetection_access_point" {
  file_system_id = aws_efs_file_system.changedetection_data.id

  posix_user {
    gid = 1000
    uid = 1000
  }

  root_directory {
    path = "/changedetection"
    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "755"
    }
  }

  tags = {
    Name = "changedetection-access-point"
  }
}

# Backup for EFS File System
resource "aws_backup_plan" "changedetection_backup_plan" {
  name = "changedetection-backup-plan"

  rule {
    rule_name         = "daily-backup"
    target_vault_name = aws_backup_vault.changedetection_backup_vault.name
    schedule          = var.backup_schedule

    lifecycle {
      delete_after = var.backup_retention_period
    }
  }

  tags = {
    Name = "changedetection-backup-plan"
  }
}

resource "aws_backup_vault" "changedetection_backup_vault" {
  name = "changedetection-backup-vault"

  tags = {
    Name = "changedetection-backup-vault"
  }
}

resource "aws_backup_selection" "changedetection_backup_selection" {
  name         = "changedetection-backup-selection"
  iam_role_arn = aws_iam_role.backup_role.arn
  plan_id      = aws_backup_plan.changedetection_backup_plan.id

  resources = [
    aws_efs_file_system.changedetection_data.arn
  ]
}
