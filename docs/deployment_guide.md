# SolarFlow ERP – Linux VPS Production Deployment Guide

**Target Environment:** Ubuntu 22.04 / 24.04 LTS x86_64  
**Stack Components:** Odoo Community (Port 8069, 8072), PostgreSQL 16-alpine (Port 5432), Nginx Reverse Proxy (Ports 80, 443), Let's Encrypt SSL.

> [!IMPORTANT]
> This guide is prepared for server readiness. Do not expose secrets or bind public DNS without proper server ownership and authorization.

---

## 1. Server Prerequisites & System Hardening

```bash
# Update and upgrade packages
sudo apt update && sudo apt upgrade -y

# Install essential dependencies
sudo apt install -y curl git ufw htop logrotate certbot python3-certbot-nginx

# Configure UFW Firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

---

## 2. Docker & Docker Compose Installation

```bash
# Add Docker official GPG key and repository
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable Docker on system boot
sudo systemctl enable --now docker
```

---

## 3. Directory Layout & Production Repository Setup

```bash
sudo mkdir -p /opt/solarflow && cd /opt/solarflow
sudo chown -R $USER:$USER /opt/solarflow

# Clone or copy SolarFlow repository
git clone https://github.com/your-org/solarflow-erp.git .
```

Directory structure on the VPS:
```
/opt/solarflow/
├── docker-compose.prod.yml
├── .env.production
├── config/
│   └── odoo.conf
├── addons/
│   └── solarflow_management/
├── nginx/
│   └── solarflow.conf
└── scripts/
    └── backup_db.sh
```

---

## 4. Production Docker Compose Configuration (`docker-compose.prod.yml`)

```yaml
version: '3.8'

services:
  solarflow-db:
    image: postgres:16-alpine
    container_name: solarflow-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - solarflow_db_prod_data:/var/lib/postgresql/data
    networks:
      - solarflow_net

  solarflow-web:
    image: odoo:18.0 # or 20.0 community build
    container_name: solarflow-web
    restart: unless-stopped
    depends_on:
      - solarflow-db
    environment:
      - HOST=solarflow-db
      - USER=${POSTGRES_USER}
      - PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - solarflow_web_prod_data:/var/lib/odoo
      - ./config:/etc/odoo
      - ./addons:/mnt/extra-addons
    expose:
      - "8069"
      - "8072"
    networks:
      - solarflow_net

volumes:
  solarflow_db_prod_data:
    driver: local
  solarflow_web_prod_data:
    driver: local

networks:
  solarflow_net:
    driver: bridge
```

---

## 5. Nginx Reverse Proxy & HTTPS (Let's Encrypt)

Create `/etc/nginx/sites-available/solarflow.conf`:

```nginx
# Upstream servers
upstream odoo_backend {
    server 127.0.0.1:8069;
}
upstream odoo_chat {
    server 127.0.0.1:8072;
}

server {
    listen 80;
    server_name erp.your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name erp.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/erp.your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/erp.your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    # Add Headers for Odoo Proxy mode
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # Odoo Longpolling
    location /longpolling {
        proxy_pass http://odoo_chat;
    }

    # Odoo Web
    location / {
        proxy_redirect off;
        proxy_pass http://odoo_backend;
    }

    # Static Cache
    location ~* /web/static/ {
        proxy_cache_valid 200 60m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo_backend;
    }

    gzip_types text/css text/less text/plain text/xml application/xml application/json application/javascript;
    gzip on;
}
```

Enable site and acquire SSL:
```bash
sudo ln -s /etc/nginx/sites-available/solarflow.conf /etc/nginx/sites-enabled/
sudo certbot --nginx -d erp.your-domain.com
sudo systemctl reload nginx
```

---

## 6. Automated Database Backup Strategy

Create `/opt/solarflow/scripts/backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/solarflow/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"

# Dump PostgreSQL database directly from container
docker exec solarflow-db pg_dump -U odoo solarflow_db | gzip > "$BACKUP_DIR/solarflow_db_$TIMESTAMP.sql.gz"

# Retain only last 14 days of backups
find "$BACKUP_DIR" -type f -name "*.sql.gz" -mtime +14 -delete
echo "[$(date)] Backup completed: solarflow_db_$TIMESTAMP.sql.gz" >> "$BACKUP_DIR/backup.log"
```
Make executable and configure in crontab:
```bash
chmod +x /opt/solarflow/scripts/backup_db.sh
# Run nightly at 2:00 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/solarflow/scripts/backup_db.sh") | crontab -
```

---

## 7. Log Management & Logrotate

Create `/etc/logrotate.d/solarflow`:
```
/opt/solarflow/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    copytruncate
}
```
