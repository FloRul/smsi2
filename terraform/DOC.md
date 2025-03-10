# ChangeDetection.io Infrastructure Documentation

## Infrastructure Architecture Diagram

```mermaid
graph TD
    %% External Users
    User([Users]) -->|HTTP/HTTPS| ALB

    %% Load Balancing
    subgraph "AWS Load Balancing"
        ALB[Application Load Balancer] -->|Forward| TG[Target Group]
        ALBSG[ALB Security Group]
    end

    %% ECS Components
    subgraph "ECS Fargate"
        ECS[ECS Cluster]
        TG --> ECSService[ECS Service]
        ECSService --> ECSTask[ECS Tasks]
        ECSSG[ECS Security Group]
    end

    %% Storage
    subgraph "Storage"
        EFS[EFS File System]
        EFSAccessPoint[EFS Access Point]
        EFS --- EFSAccessPoint
        EFSMountTargets[EFS Mount Targets]
        EFS --- EFSMountTargets
        EFSSG[EFS Security Group]
    end

    %% Networking
    subgraph "Networking"
        VPC[VPC: 10.0.0.0/16]
        IGW[Internet Gateway]
        PublicSubnet1[Public Subnet 1: 10.0.1.0/24]
        PublicSubnet2[Public Subnet 2: 10.0.2.0/24]
        
        VPC --- IGW
        VPC --- PublicSubnet1
        VPC --- PublicSubnet2
    end

    %% Security and IAM
    subgraph "Security & IAM"
        IAMExecutionRole[IAM Execution Role]
        IAMTaskRole[IAM Task Role]
        BackupRole[Backup Role]
    end

    %% Monitoring & Logging
    subgraph "Monitoring"
        CWLogs[CloudWatch Logs]
        CWAlarms[CloudWatch Alarms]
        CWDashboard[CloudWatch Dashboard]
    end

    %% Backup
    subgraph "Backup"
        BackupPlan[AWS Backup Plan]
        BackupVault[Backup Vault]
        BackupPlan --- BackupVault
    end

    %% Connections
    ECSTask --> EFS
    ECSTask -.-> CWLogs
    EFS -.-> BackupPlan
    ECSTask --- IAMTaskRole
    ECSService --- IAMExecutionRole
    BackupPlan --- BackupRole
    
    %% Security Group Relationships
    ALBSG -->|Allows| ECSSG
    ECSSG -->|Allows| EFSSG
    
    %% Placement in VPC
    PublicSubnet1 -.->|Hosts| ALB
    PublicSubnet2 -.->|Hosts| ALB
    PublicSubnet1 -.->|Hosts| ECSTask
    PublicSubnet2 -.->|Hosts| ECSTask
    PublicSubnet1 -.->|Hosts| EFSMountTargets
    PublicSubnet2 -.->|Hosts| EFSMountTargets
```

## Infrastructure Details

### Networking
- **VPC**: CIDR 10.0.0.0/16
- **Public Subnets**: 2 subnets across different AZs
- **Internet Gateway**: For public internet access

### Compute
- **ECS Cluster**: Runs on AWS Fargate (serverless)
- **ECS Service**: Maintains desired task count
- **Container**: ChangeDetection.io application

### Storage
- **EFS File System**: Persistent storage for application data
- **Mount Targets**: In both public subnets
- **Daily Backups**: Using AWS Backup

### Security
- **ALB Security Group**: Allows HTTP on port 5000 from whitelisted IPs
- **ECS Security Group**: Permits traffic only from the load balancer
- **EFS Security Group**: Allows NFS traffic from ECS tasks
- **IAM Roles**: Least privilege permissions for each component

### Load Balancing
- **Application Load Balancer**: Distributes traffic to ECS tasks
- **Target Group**: With health checks to ensure application availability
- **HTTP Listener**: On port 80 (with potential for HTTPS configuration)

### Monitoring
- **CloudWatch Logs**: For container log management
- **CloudWatch Dashboard**: With CPU and memory metrics
- **CloudWatch Alarms**: For high resource utilization

## Key Design Elements
- **High Availability**: Resources deployed across multiple AZs
- **Security**: Layered security with specific network rules
- **Data Persistence**: EFS with backup for data durability
- **Scalability**: ECS services can scale based on demand