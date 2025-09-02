# CodeCrafts MVP - Production Deployment Guide

This guide provides comprehensive instructions for deploying CodeCrafts MVP to a production environment using Docker and Docker Compose.

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / Amazon Linux 2
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB, Recommended 50GB+ SSD
- **CPU**: Minimum 2 cores, Recommended 4+ cores
- **Network**: Public IP address and domain name

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Git
- SSL certificate (Let's Encrypt recommended)

## Quick Start

### 1. Server Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply Docker group changes
```

### 2. Clone Repository

```bash
git clone https://github.com/your-org/codecrafts-mvp.git
cd codecrafts-mvp
```

### 3. Environment Configuration

```bash
# Copy production environment template
cp .env.production .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**

```bash
# Domain and SSL
DOMAIN_NAME=your-domain.com
SSL_EMAIL=admin@your-domain.com

# Database
POSTGRES_PASSWORD=your_secure_database_password
REDIS_PASSWORD=your_secure_redis_password

# Security
SECRET_KEY=your_very_secure_secret_key_at_least_32_characters
JWT_SECRET_KEY=your_jwt_secret_key_different_from_secret_key

# Admin User
ADMIN_EMAIL=admin@your-domain.com
ADMIN_PASSWORD=your_secure_admin_password
```

### 4. Deploy Application

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### 5. Setup SSL Certificates

```bash
# Obtain SSL certificates (after DNS is configured)
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email your-email@domain.com --agree-tos --no-eff-email \
  -d your-domain.com

# Reload Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## Detailed Configuration

### Environment Variables Reference

#### Core Configuration
```bash
# Application
ENV=production
DOMAIN_NAME=codecrafts.app
SSL_EMAIL=admin@codecrafts.app

# Database
POSTGRES_DB=codecrafts_prod
POSTGRES_USER=codecrafts
POSTGRES_PASSWORD=secure_password_here

# Redis
REDIS_PASSWORD=secure_redis_password

# Security
SECRET_KEY=your_32_character_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_different_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Optional Configuration
```bash
# External Services
JUDGE0_API_URL=http://judge0:2358
SENTRY_DSN=your_sentry_dsn_for_error_tracking

# Performance
WORKER_PROCESSES=4
MAX_CONNECTIONS=1000
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=60

# Features
ENABLE_REGISTRATION=true
ENABLE_DUELS=true
ENABLE_CODE_EXECUTION=true
ENABLE_MONITORING=false

# Backup
BACKUP_ENABLED=true
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=codecrafts-backups
```

### DNS Configuration

Point your domain to your server's IP address:

```
A     @              YOUR_SERVER_IP
A     www            YOUR_SERVER_IP
AAAA  @              YOUR_SERVER_IPv6  (if available)
AAAA  www            YOUR_SERVER_IPv6  (if available)
```

### Firewall Configuration

```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

## Service Architecture

### Container Services

1. **nginx** - Reverse proxy and SSL termination
2. **frontend** - React application served by Nginx
3. **backend** - FastAPI application with Gunicorn
4. **db** - PostgreSQL database
5. **redis** - Redis cache and session store
6. **judge0** - Code execution service (optional)
7. **certbot** - SSL certificate management

### Network Architecture

```
Internet → Nginx (80/443) → Frontend (80) / Backend (8000)
                         ↓
                    PostgreSQL (5432)
                         ↓
                    Redis (6379)
                         ↓
                    Judge0 (2358)
```

### Data Persistence

- **postgres_data**: Database files
- **redis_data**: Redis persistence
- **nginx_logs**: Nginx access and error logs
- **certbot_data**: Let's Encrypt challenge files
- **certbot_conf**: SSL certificates

## Monitoring and Maintenance

### Health Checks

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Check service health
curl -f https://your-domain.com/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f [service_name]
```

### Backup and Restore

#### Automated Backups

Backups are automatically created during deployment. Manual backup:

```bash
# Create backup
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh /path/to/backup
```

#### Database Backup

```bash
# Manual database backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U codecrafts codecrafts_prod > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T db psql -U codecrafts codecrafts_prod < backup.sql
```

### SSL Certificate Renewal

SSL certificates are automatically renewed. Manual renewal:

```bash
# Renew certificates
docker-compose -f docker-compose.prod.yml run --rm certbot renew

# Reload Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Updates and Maintenance

#### Application Updates

```bash
# Pull latest code
git pull origin main

# Redeploy with backup
./scripts/deploy.sh

# Or deploy without backup (faster)
./scripts/deploy.sh --skip-backup
```

#### System Maintenance

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean up Docker resources
docker system prune -f

# Monitor disk usage
df -h
docker system df
```

## Performance Optimization

### Database Optimization

```sql
-- Monitor slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Update statistics
ANALYZE;

-- Vacuum database
VACUUM ANALYZE;
```

### Application Performance

```bash
# Monitor resource usage
docker stats

# Check application metrics
curl https://your-domain.com/metrics

# Monitor logs for errors
docker-compose -f docker-compose.prod.yml logs backend | grep ERROR
```

### Nginx Optimization

```nginx
# Already configured in nginx.conf:
# - Gzip compression
# - Static file caching
# - Rate limiting
# - Security headers
```

## Security Considerations

### Security Checklist

- [ ] Strong passwords for all services
- [ ] SSL certificates properly configured
- [ ] Firewall rules configured
- [ ] Regular security updates
- [ ] Database access restricted
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Backup encryption enabled

### Security Headers

The following security headers are automatically configured:

- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `X-XSS-Protection`
- `Referrer-Policy`

### Access Control

```bash
# Restrict database access
# Only allow connections from application containers

# Monitor failed login attempts
docker-compose -f docker-compose.prod.yml logs nginx | grep "401\|403"

# Check for suspicious activity
docker-compose -f docker-compose.prod.yml logs backend | grep "rate limit"
```

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check service logs
docker-compose -f docker-compose.prod.yml logs [service_name]

# Check service health
docker-compose -f docker-compose.prod.yml ps

# Restart specific service
docker-compose -f docker-compose.prod.yml restart [service_name]
```

#### Database Connection Issues

```bash
# Check database logs
docker-compose -f docker-compose.prod.yml logs db

# Test database connection
docker-compose -f docker-compose.prod.yml exec backend python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
print('Database connection successful')
"
```

#### SSL Certificate Issues

```bash
# Check certificate status
docker-compose -f docker-compose.prod.yml exec nginx openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -text -noout

# Test SSL configuration
curl -I https://your-domain.com

# Renew certificates manually
docker-compose -f docker-compose.prod.yml run --rm certbot renew --force-renewal
```

#### Performance Issues

```bash
# Check resource usage
docker stats

# Monitor database performance
docker-compose -f docker-compose.prod.yml exec db psql -U codecrafts -d codecrafts_prod -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';
"

# Check application logs for slow requests
docker-compose -f docker-compose.prod.yml logs backend | grep "slow"
```

### Log Analysis

```bash
# Application errors
docker-compose -f docker-compose.prod.yml logs backend | grep ERROR

# Database errors
docker-compose -f docker-compose.prod.yml logs db | grep ERROR

# Nginx access logs
docker-compose -f docker-compose.prod.yml logs nginx | tail -100

# Rate limiting logs
docker-compose -f docker-compose.prod.yml logs nginx | grep "limiting"
```

## Scaling Considerations

### Horizontal Scaling

To scale the application horizontally:

1. **Load Balancer**: Add a load balancer in front of multiple application instances
2. **Database**: Consider read replicas for database scaling
3. **Redis Cluster**: Use Redis cluster for session storage
4. **CDN**: Use a CDN for static asset delivery

### Vertical Scaling

```bash
# Increase container resources in docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Monitoring Setup (Optional)

### Enable Monitoring

```bash
# Start monitoring services
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Access Grafana
https://your-domain.com:3000
# Default login: admin / [GRAFANA_PASSWORD from .env]
```

### Metrics Available

- Application performance metrics
- Database performance
- System resource usage
- Error rates and response times
- User activity metrics

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Review application logs
   - Check disk space usage
   - Verify backup integrity

2. **Monthly**:
   - Update system packages
   - Review security logs
   - Performance optimization

3. **Quarterly**:
   - Security audit
   - Capacity planning
   - Disaster recovery testing

### Getting Help

- Check application logs first
- Review this documentation
- Check GitHub issues
- Contact support team

---

## Quick Reference Commands

```bash
# Deploy application
./scripts/deploy.sh

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart service
docker-compose -f docker-compose.prod.yml restart [service]

# Update application
git pull && ./scripts/deploy.sh

# Backup database
./scripts/backup.sh

# Renew SSL
docker-compose -f docker-compose.prod.yml run --rm certbot renew
```

This deployment guide ensures a secure, scalable, and maintainable production environment for CodeCrafts MVP.