#!/bin/bash

# Function to print status messages
print_status() {
    echo "=== $1 ==="
}

# Stop services
print_status "Stopping Services"
systemctl stop openresty
systemctl stop elasticsearch
systemctl stop docker
systemctl stop docker.socket

# Remove OpenResty configuration and files
print_status "Removing OpenResty"
rm -rf /usr/local/openresty
rm -f /etc/systemd/system/openresty.service
rm -rf /var/log/openresty
rm -rf /etc/nginx
systemctl daemon-reload

# Remove web application files
print_status "Removing Web Application"
rm -rf /var/www/valeros

# Remove SSL certificates
print_status "Removing SSL Certificates"
rm -rf /etc/nginx/ssl
rm -rf /etc/letsencrypt

# Remove Docker containers and images
print_status "Cleaning Docker"
docker rm -f $(docker ps -aq) 2>/dev/null || true
docker rmi -f $(docker images -aq) 2>/dev/null || true
docker volume rm $(docker volume ls -q) 2>/dev/null || true
docker network prune -f

# Remove Docker itself
print_status "Removing Docker"
apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
rm -rf /var/lib/docker
rm -rf /var/lib/containerd

# Remove Elasticsearch
print_status "Removing Elasticsearch"
apt-get remove -y elasticsearch
rm -rf /var/lib/elasticsearch
rm -rf /etc/elasticsearch
rm -rf /var/log/elasticsearch

# Remove Python virtual environment
print_status "Removing Python Environment"
rm -rf /opt/venv

# Remove other installed packages
print_status "Removing Installed Packages"
apt-get remove -y git certbot python3-certbot-nginx ufw
apt-get autoremove -y

# Remove firewall rules
print_status "Removing Firewall Rules"
ufw delete allow 80/tcp
ufw delete allow 443/tcp

# Clean package cache
print_status "Cleaning Package Cache"
apt-get clean
apt-get autoclean

# Final cleanup
print_status "Final Cleanup"
rm -rf /opt/deployscripts*
rm -rf /tmp/*

print_status "Teardown Complete"
echo "Note: You may need to reboot the system for all changes to take effect."
