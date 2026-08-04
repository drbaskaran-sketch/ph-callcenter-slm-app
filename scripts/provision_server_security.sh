#!/bin/bash
# =====================================================================
# PRASHANTH HOSPITALS — SERVER PROVISIONING & SECURITY HARDENING SCRIPT
# =====================================================================

set -e

NEW_USER=${1:-"deployuser"}
SSH_PUB_KEY=${2:-""}

echo "=========================================================================="
echo "🛡️  STARTING SERVER PROVISIONING & HARDENING FOR $NEW_USER"
echo "=========================================================================="

# 1. Create Non-Root System User with Sudo Privileges
if id "$NEW_USER" &>/dev/null; then
    echo "ℹ️ User $NEW_USER already exists."
else
    echo "1️⃣  Creating non-root user $NEW_USER with sudo privileges..."
    sudo useradd -m -s /bin/bash "$NEW_USER"
    sudo usermod -aG sudo "$NEW_USER"
    echo "$NEW_USER ALL=(ALL) NOPASSWD:ALL" | sudo tee "/etc/sudoers.d/$NEW_USER"
    echo "✅ User $NEW_USER created and added to sudoers."
fi

# 2. Configure SSH Key-Based Authentication
echo "2️⃣  Configuring SSH Key-Based Authentication for $NEW_USER..."
USER_HOME=$(eval echo "~$NEW_USER")
sudo mkdir -p "$USER_HOME/.ssh"
sudo chmod 700 "$USER_HOME/.ssh"

if [ -n "$SSH_PUB_KEY" ]; then
    echo "$SSH_PUB_KEY" | sudo tee "$USER_HOME/.ssh/authorized_keys" > /dev/null
    sudo chmod 600 "$USER_HOME/.ssh/authorized_keys"
    echo "✅ SSH public key added to $USER_HOME/.ssh/authorized_keys"
else
    # Copy current user's authorized_keys if present
    if [ -f "$HOME/.ssh/authorized_keys" ]; then
        sudo cp "$HOME/.ssh/authorized_keys" "$USER_HOME/.ssh/authorized_keys"
        sudo chmod 600 "$USER_HOME/.ssh/authorized_keys"
        echo "✅ Current SSH public key copied to $USER_HOME/.ssh/authorized_keys"
    fi
fi

sudo chown -R "$NEW_USER:$NEW_USER" "$USER_HOME/.ssh"

# 3. Harden SSH Daemon Configuration (/etc/ssh/sshd_config)
echo "3️⃣  Hardening SSH Daemon (Disabling Root Login & Password Auth)..."
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config 2>/dev/null || true
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config 2>/dev/null || true
sudo sed -i 's/^#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config 2>/dev/null || true

# 4. Configure Uncomplicated Firewall (UFW) Strict Policy
echo "4️⃣  Configuring Strict UFW Firewall Rules..."
if command -v ufw &> /dev/null; then
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow 22/tcp comment 'SSH Port'
    sudo ufw allow 80/tcp comment 'HTTP Web Port'
    sudo ufw allow 443/tcp comment 'HTTPS Secure Web Port'
    sudo ufw allow 5173/tcp comment 'Vite React Frontend'
    sudo ufw allow 8000/tcp comment 'FastAPI Backend API'
    sudo ufw --force enable
    echo "✅ UFW Firewall enabled with strict incoming restrictions."
else
    echo "ℹ️ UFW utility not installed. Security group rules managed via AWS/Cloud Provider."
fi

# 5. Install & Enable Fail2ban for Brute-Force Defense
echo "5️⃣  Configuring Fail2ban Brute-Force Prevention..."
if command -v systemctl &> /dev/null && command -v apt-get &> /dev/null; then
    sudo apt-get update -qq && sudo apt-get install -y -qq fail2ban
    sudo systemctl enable fail2ban --now 2>/dev/null || true
    echo "✅ Fail2ban service enabled for SSH brute-force defense."
fi

echo "=========================================================================="
echo "✨ SERVER HARDENING COMPLETED SUCCESSFULLY FOR $NEW_USER"
echo "=========================================================================="
