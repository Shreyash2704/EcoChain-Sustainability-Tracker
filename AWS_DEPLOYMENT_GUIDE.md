# 🚀 AWS Deployment Guide for EcoChain

## **📋 Overview**

This guide covers deploying EcoChain to AWS using Docker containers with ECS (Elastic Container Service), RDS (Relational Database Service), and other AWS services.

## **🏗️ AWS Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CloudFront    │    │   ECS Cluster   │    │   RDS Database  │
│   (CDN)         │◄──►│   (Containers)  │◄──►│   (PostgreSQL)  │
│                 │    │                 │    │                 │
│ • Global CDN     │    │ • Backend      │    │ • Multi-AZ     │
│ • SSL/HTTPS    │    │ • Frontend      │    │ • Backups      │
│ • Caching      │    │ • AI Agents     │    │ • Encryption   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Route 53      │    │   ElastiCache    │    │   S3 Storage    │
│   (DNS)         │    │   (Redis)        │    │   (IPFS)        │
│                 │    │                 │    │                 │
│ • Domain        │    │ • Caching       │    │ • File Storage  │
│ • Health Checks │    │ • Sessions      │    │ • Backups       │
│ • Failover      │    │ • Performance   │    │ • Static Assets │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## **🔧 AWS Services Required**

### **Core Services**
- **ECS (Elastic Container Service)** - Container orchestration
- **ECR (Elastic Container Registry)** - Docker image storage
- **RDS (Relational Database Service)** - PostgreSQL database
- **ElastiCache** - Redis caching
- **S3** - File storage and backups
- **CloudFront** - CDN and SSL termination
- **Route 53** - DNS management
- **ALB (Application Load Balancer)** - Load balancing

### **Optional Services**
- **Secrets Manager** - Secure environment variables
- **CloudWatch** - Monitoring and logging
- **SNS** - Notifications and alerts
- **Lambda** - Serverless functions
- **API Gateway** - API management

## **📦 Container Setup**

### **1. Build and Push Images to ECR**

```bash
#!/bin/bash
# build-and-push.sh

# Set variables
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=your-account-id
ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
REPOSITORY_NAME=ecochain

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

# Create ECR repositories
aws ecr create-repository --repository-name $REPOSITORY_NAME-backend --region $AWS_REGION
aws ecr create-repository --repository-name $REPOSITORY_NAME-frontend --region $AWS_REGION
aws ecr create-repository --repository-name $REPOSITORY_NAME-metta --region $AWS_REGION

# Build and push backend
cd backend
docker build -t $REPOSITORY_NAME-backend .
docker tag $REPOSITORY_NAME-backend:latest $ECR_REGISTRY/$REPOSITORY_NAME-backend:latest
docker push $ECR_REGISTRY/$REPOSITORY_NAME-backend:latest

# Build and push frontend
cd ../client
docker build -t $REPOSITORY_NAME-frontend .
docker tag $REPOSITORY_NAME-frontend:latest $ECR_REGISTRY/$REPOSITORY_NAME-frontend:latest
docker push $ECR_REGISTRY/$REPOSITORY_NAME-frontend:latest

# Build and push MeTTa service
cd ../metta
docker build -t $REPOSITORY_NAME-metta .
docker tag $REPOSITORY_NAME-metta:latest $ECR_REGISTRY/$REPOSITORY_NAME-metta:latest
docker push $ECR_REGISTRY/$REPOSITORY_NAME-metta:latest

echo "✅ All images pushed to ECR!"
```

### **2. ECS Task Definitions**

```json
{
  "family": "ecochain-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/ecochain-backend:latest",
      "portMappings": [
        {
          "containerPort": 8002,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:ecochain/database"
        },
        {
          "name": "PRIVATE_KEY",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:ecochain/private-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ecochain-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8002/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

## **🗄️ Database Setup**

### **RDS PostgreSQL Configuration**

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier ecochain-production \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 14.7 \
  --master-username ecochain_admin \
  --master-user-password your-secure-password \
  --allocated-storage 100 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name ecochain-db-subnet-group \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted \
  --deletion-protection
```

### **ElastiCache Redis Configuration**

```bash
# Create ElastiCache cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id ecochain-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --cache-subnet-group-name ecochain-cache-subnet-group
```

## **🌐 Load Balancer Setup**

### **Application Load Balancer**

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name ecochain-alb \
  --subnets subnet-xxxxxxxxx subnet-yyyyyyyyy \
  --security-groups sg-xxxxxxxxx \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4
```

### **Target Groups**

```bash
# Create target group for backend
aws elbv2 create-target-group \
  --name ecochain-backend-tg \
  --protocol HTTP \
  --port 8002 \
  --vpc-id vpc-xxxxxxxxx \
  --target-type ip \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3
```

## **🚀 ECS Service Deployment**

### **ECS Cluster Creation**

```bash
# Create ECS cluster
aws ecs create-cluster \
  --cluster-name ecochain-cluster \
  --capacity-providers FARGATE \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1
```

### **Service Definition**

```json
{
  "serviceName": "ecochain-backend",
  "cluster": "ecochain-cluster",
  "taskDefinition": "ecochain-backend",
  "desiredCount": 2,
  "launchType": "FARGATE",
  "networkConfiguration": {
    "awsvpcConfiguration": {
      "subnets": ["subnet-xxxxxxxxx", "subnet-yyyyyyyyy"],
      "securityGroups": ["sg-xxxxxxxxx"],
      "assignPublicIp": "ENABLED"
    }
  },
  "loadBalancers": [
    {
      "targetGroupArn": "arn:aws:elasticloadbalancing:REGION:ACCOUNT:targetgroup/ecochain-backend-tg/ID",
      "containerName": "backend",
      "containerPort": 8002
    }
  ],
  "healthCheckGracePeriodSeconds": 300,
  "deploymentConfiguration": {
    "maximumPercent": 200,
    "minimumHealthyPercent": 50
  }
}
```

## **🔐 Security Configuration**

### **IAM Roles and Policies**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "rds:DescribeDBInstances",
        "elasticache:DescribeCacheClusters",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "*"
    }
  ]
}
```

### **Security Groups**

```bash
# Create security group for ALB
aws ec2 create-security-group \
  --group-name ecochain-alb-sg \
  --description "Security group for EcoChain ALB" \
  --vpc-id vpc-xxxxxxxxx

# Allow HTTP/HTTPS traffic
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

## **📊 Monitoring Setup**

### **CloudWatch Logs**

```bash
# Create log groups
aws logs create-log-group \
  --log-group-name /ecs/ecochain-backend

aws logs create-log-group \
  --log-group-name /ecs/ecochain-frontend

aws logs create-log-group \
  --log-group-name /ecs/ecochain-metta
```

### **CloudWatch Alarms**

```bash
# Create CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name ecochain-high-cpu \
  --alarm-description "High CPU utilization" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

## **🌍 CDN and SSL Setup**

### **CloudFront Distribution**

```json
{
  "CallerReference": "ecochain-distribution",
  "Comment": "EcoChain CDN Distribution",
  "DefaultCacheBehavior": {
    "TargetOriginId": "ecochain-alb",
    "ViewerProtocolPolicy": "redirect-to-https",
    "TrustedSigners": {
      "Enabled": false,
      "Quantity": 0
    },
    "ForwardedValues": {
      "QueryString": true,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000
  },
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "ecochain-alb",
        "DomainName": "ecochain-alb-1234567890.us-east-1.elb.amazonaws.com",
        "CustomOriginConfig": {
          "HTTPPort": 80,
          "HTTPSPort": 443,
          "OriginProtocolPolicy": "https-only"
        }
      }
    ]
  },
  "Enabled": true,
  "PriceClass": "PriceClass_100"
}
```

## **🚀 Deployment Scripts**

### **Complete Deployment Script**

```bash
#!/bin/bash
# deploy-to-aws.sh

set -e

# Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "🚀 Starting EcoChain deployment to AWS..."

# 1. Build and push images
echo "📦 Building and pushing Docker images..."
./scripts/build-and-push.sh

# 2. Create ECS cluster
echo "🏗️ Creating ECS cluster..."
aws ecs create-cluster --cluster-name ecochain-cluster --capacity-providers FARGATE

# 3. Create RDS instance
echo "🗄️ Creating RDS database..."
./scripts/create-rds.sh

# 4. Create ElastiCache
echo "⚡ Creating ElastiCache Redis..."
./scripts/create-elasticache.sh

# 5. Create load balancer
echo "⚖️ Creating Application Load Balancer..."
./scripts/create-alb.sh

# 6. Deploy ECS services
echo "🚀 Deploying ECS services..."
./scripts/deploy-ecs-services.sh

# 7. Create CloudFront distribution
echo "🌍 Creating CloudFront distribution..."
./scripts/create-cloudfront.sh

# 8. Configure Route 53
echo "🌐 Configuring Route 53..."
./scripts/configure-route53.sh

echo "✅ EcoChain deployment complete!"
echo "🌐 Application URL: https://ecochain.app"
```

## **💰 Cost Estimation**

### **Monthly AWS Costs (Estimated)**

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **ECS Fargate** | 2 tasks, 1 vCPU, 2GB RAM | $30-50 |
| **RDS PostgreSQL** | db.t3.medium, Multi-AZ | $60-80 |
| **ElastiCache Redis** | cache.t3.micro | $15-25 |
| **Application Load Balancer** | Standard | $20-30 |
| **CloudFront** | 1TB transfer | $85-100 |
| **Route 53** | Hosted zone + queries | $1-5 |
| **S3** | 100GB storage | $3-5 |
| **CloudWatch** | Logs + metrics | $10-20 |
| **Total** | | **$224-315/month** |

## **📋 Deployment Checklist**

- [ ] **AWS Account Setup** with proper permissions
- [ ] **ECR Repositories** created
- [ ] **Docker Images** built and pushed
- [ ] **RDS Database** configured
- [ ] **ElastiCache Redis** configured
- [ ] **ECS Cluster** created
- [ ] **Load Balancer** configured
- [ ] **Security Groups** configured
- [ ] **IAM Roles** created
- [ ] **CloudWatch** monitoring setup
- [ ] **CloudFront** CDN configured
- [ ] **Route 53** DNS configured
- [ ] **SSL Certificates** installed
- [ ] **Health Checks** configured
- [ ] **Backup Strategy** implemented

---

**This AWS deployment strategy provides a scalable, secure, and cost-effective solution for EcoChain using Docker containers and AWS managed services!**
