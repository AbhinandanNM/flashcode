#!/bin/sh

set -e

echo "Starting Nginx with SSL configuration..."

# Check if Let's Encrypt certificates exist
if [ -f "/etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem" ]; then
    echo "Using Let's Encrypt certificates for ${DOMAIN_NAME}"
    # Update nginx config to use Let's Encrypt certificates
    sed -i "s|ssl_certificate /etc/nginx/ssl/selfsigned.crt;|ssl_certificate /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem;|g" /etc/nginx/conf.d/default.conf
    sed -i "s|ssl_certificate_key /etc/nginx/ssl/selfsigned.key;|ssl_certificate_key /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem;|g" /etc/nginx/conf.d/default.conf
else
    echo "Let's Encrypt certificates not found, using self-signed certificates"
    echo "To obtain SSL certificates, run: docker-compose exec certbot certbot certonly --webroot --webroot-path=/var/www/certbot --email ${SSL_EMAIL} --agree-tos --no-eff-email -d ${DOMAIN_NAME}"
fi

# Test nginx configuration
nginx -t

# Start nginx
exec "$@"