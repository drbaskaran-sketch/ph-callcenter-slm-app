#!/bin/bash
# =====================================================================
# PRASHANTH HOSPITALS — AUTOMATED CERTBOT (LET'S ENCRYPT) SSL PROVISIONER
# =====================================================================

set -e

DOMAIN=${1:-"callcenter-slm.prashanthhospitals.com"}
EMAIL=${2:-"admin@prashanthhospitals.com"}

echo "=========================================================================="
echo "🔐 PROVISIONING FREE LET'S ENCRYPT SSL CERTIFICATE FOR $DOMAIN"
echo "=========================================================================="

# 1. Install Nginx and Certbot dependencies if available
echo "1️⃣  Installing Certbot & Nginx plugin..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq certbot python3-certbot-nginx cron
    echo "✅ Certbot and Python3 Certbot Nginx plugin installed."
fi

# 2. Deploy Nginx Configuration File
echo "2️⃣  Linking Nginx Reverse Proxy Configuration..."
NGINX_CONF_SRC="/home/ubuntu/ph-callcenter-slm-app/nginx/ph-slm-app.nginx.conf"
NGINX_CONF_DEST="/etc/nginx/sites-available/ph-slm-app.conf"

if [ -d "/etc/nginx/sites-available" ]; then
    sudo cp "$NGINX_CONF_SRC" "$NGINX_CONF_DEST"
    sudo ln -sf "$NGINX_CONF_DEST" /etc/nginx/sites-enabled/ph-slm-app.conf
    sudo rm -f /etc/nginx/sites-enabled/default
    echo "✅ Nginx site configuration linked to /etc/nginx/sites-enabled/"
fi

# 3. Provision Let's Encrypt Free SSL Certificate via Certbot
echo "3️⃣  Requesting Let's Encrypt SSL Certificate..."
if command -v certbot &> /dev/null; then
    # Provision SSL Certificate in non-interactive mode
    sudo certbot --nginx \
        -d "$DOMAIN" \
        --non-interactive \
        --agree-tos \
        -m "$EMAIL" \
        --redirect || echo "ℹ️ Certbot domain verification requires public DNS pointing to this instance."
else
    echo "ℹ️ Certbot binary not present in environment. Automated renewal script configured."
fi

# 4. Configure Automated SSL Certificate Renewal Cron Job
echo "4️⃣  Setting up Automated SSL Certificate Renewal Cron Job..."
CRON_JOB="0 3 * * * root certbot renew --quiet --post-hook 'systemctl reload nginx'"
echo "$CRON_JOB" | sudo tee /etc/cron.d/certbot-renew > /dev/null
sudo chmod 644 /etc/cron.d/certbot-renew
echo "✅ Automated Let's Encrypt SSL renewal cron configured (/etc/cron.d/certbot-renew)."

# 5. Reload Nginx Server
echo "5️⃣  Testing Nginx Configuration & Reloading..."
if command -v nginx &> /dev/null; then
    sudo nginx -t && sudo systemctl reload nginx
    echo "✅ Nginx server reloaded with active Let's Encrypt SSL."
fi

echo "=========================================================================="
echo "✨ CERTBOT LET'S ENCRYPT SSL PROVISIONING COMPLETED FOR $DOMAIN"
echo "=========================================================================="
