#!/bin/bash

set -e

# CodeCrafts MVP Production Deployment Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deploy.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Create necessary directories
mkdir -p logs backups

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        error "Environment file $ENV_FILE not found. Please copy .env.production to .env and configure it."
    fi
    
    # Check if required environment variables are set
    source "$ENV_FILE"
    
    required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "SECRET_KEY"
        "JWT_SECRET_KEY"
        "DOMAIN_NAME"
        "SSL_EMAIL"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            error "Required environment variable $var is not set in $ENV_FILE"
        fi
    done
    
    success "Prerequisites check passed"
}

# Backup database
backup_database() {
    if [ "$1" = "--skip-backup" ]; then
        warning "Skipping database backup as requested"
        return
    fi
    
    log "Creating database backup..."
    
    # Create backup directory with timestamp
    BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
    mkdir -p "$BACKUP_PATH"
    
    # Check if database container is running
    if docker-compose -f "$COMPOSE_FILE" ps db | grep -q "Up"; then
        # Create database dump
        docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_PATH/database.sql"
        
        # Backup uploaded files and logs
        docker-compose -f "$COMPOSE_FILE" exec -T backend tar -czf - /app/uploads /app/logs > "$BACKUP_PATH/files.tar.gz" 2>/dev/null || true
        
        success "Database backup created at $BACKUP_PATH"
    else
        warning "Database container not running, skipping backup"
    fi
}

# Pull latest images
pull_images() {
    log "Pulling latest Docker images..."
    docker-compose -f "$COMPOSE_FILE" pull
    success "Images pulled successfully"
}

# Build custom images
build_images() {
    log "Building custom Docker images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    success "Images built successfully"
}

# Deploy application
deploy() {
    log "Deploying CodeCrafts MVP..."
    
    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose -f "$COMPOSE_FILE" down
    
    # Start new containers
    log "Starting new containers..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    check_health
    
    success "Deployment completed successfully"
}

# Check service health
check_health() {
    log "Checking service health..."
    
    services=("db" "redis" "backend" "frontend" "nginx")
    
    for service in "${services[@]}"; do
        log "Checking $service..."
        
        # Wait up to 60 seconds for service to be healthy
        timeout=60
        while [ $timeout -gt 0 ]; do
            if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy\|Up"; then
                success "$service is healthy"
                break
            fi
            
            sleep 5
            timeout=$((timeout - 5))
        done
        
        if [ $timeout -le 0 ]; then
            warning "$service health check timed out"
            docker-compose -f "$COMPOSE_FILE" logs "$service" | tail -20
        fi
    done
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    # Check if certificates already exist
    if docker-compose -f "$COMPOSE_FILE" exec nginx test -f "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"; then
        log "SSL certificates already exist for $DOMAIN_NAME"
        return
    fi
    
    # Obtain SSL certificates
    log "Obtaining SSL certificates for $DOMAIN_NAME..."
    docker-compose -f "$COMPOSE_FILE" run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$SSL_EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN_NAME"
    
    # Reload nginx to use new certificates
    docker-compose -f "$COMPOSE_FILE" exec nginx nginx -s reload
    
    success "SSL certificates configured successfully"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Wait for backend to be ready
    sleep 10
    
    # Run migrations
    docker-compose -f "$COMPOSE_FILE" exec backend alembic upgrade head
    
    success "Database migrations completed"
}

# Setup monitoring (optional)
setup_monitoring() {
    if [ "$ENABLE_MONITORING" = "true" ]; then
        log "Setting up monitoring..."
        docker-compose -f "$COMPOSE_FILE" --profile monitoring up -d
        success "Monitoring services started"
    else
        log "Monitoring disabled, skipping setup"
    fi
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old Docker images and containers..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused volumes (be careful with this)
    if [ "$1" = "--cleanup-volumes" ]; then
        warning "Cleaning up unused volumes..."
        docker volume prune -f
    fi
    
    success "Cleanup completed"
}

# Show deployment status
show_status() {
    log "Deployment Status:"
    echo "===================="
    
    # Show running containers
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    log "Service URLs:"
    echo "Frontend: https://$DOMAIN_NAME"
    echo "API: https://$DOMAIN_NAME/api"
    echo "Health Check: https://$DOMAIN_NAME/health"
    
    if [ "$ENABLE_MONITORING" = "true" ]; then
        echo "Grafana: https://$DOMAIN_NAME:3000"
    fi
}

# Main deployment function
main() {
    log "Starting CodeCrafts MVP deployment..."
    
    # Parse command line arguments
    SKIP_BACKUP=false
    SKIP_SSL=false
    CLEANUP_VOLUMES=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            --skip-ssl)
                SKIP_SSL=true
                shift
                ;;
            --cleanup-volumes)
                CLEANUP_VOLUMES=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --skip-backup      Skip database backup"
                echo "  --skip-ssl         Skip SSL certificate setup"
                echo "  --cleanup-volumes  Clean up unused Docker volumes"
                echo "  --help             Show this help message"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
    
    # Run deployment steps
    check_prerequisites
    
    if [ "$SKIP_BACKUP" = false ]; then
        backup_database
    fi
    
    pull_images
    build_images
    deploy
    run_migrations
    
    if [ "$SKIP_SSL" = false ]; then
        setup_ssl
    fi
    
    setup_monitoring
    
    if [ "$CLEANUP_VOLUMES" = true ]; then
        cleanup --cleanup-volumes
    else
        cleanup
    fi
    
    show_status
    
    success "CodeCrafts MVP deployment completed successfully!"
    log "Check the logs with: docker-compose -f $COMPOSE_FILE logs -f"
}

# Handle script interruption
trap 'error "Deployment interrupted"' INT TERM

# Run main function
main "$@"