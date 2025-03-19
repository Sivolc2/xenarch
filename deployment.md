# XenArch Deployment Guide for Digital Ocean

This guide covers deploying the XenArch Terrain Analysis application on a Digital Ocean droplet.

## 1. Create a Digital Ocean Droplet

1. Log in to your Digital Ocean account
2. Click "Create" and select "Droplets"
3. Choose the following settings:
   - **Distribution**: Ubuntu 22.04 LTS
   - **Plan**: Basic Shared CPU (recommended at least 2GB RAM/1 CPU)
   - **Region**: Choose a region close to your users
   - **Authentication**: SSH keys (recommended) or password
   - **Hostname**: xenarch-app (or your preferred name)
4. Click "Create Droplet"

## 2. Connect to Your Droplet

```bash
ssh root@your_droplet_ip
```

## 3. Update System and Install Dependencies

```bash
# Update package lists
apt update

# Install system dependencies
apt install -y python3-pip python3-venv nginx supervisor

# Install GDAL dependencies
apt install -y gdal-bin libgdal-dev
```

## 4. Set Up Project Structure

```bash
# Create application directory
mkdir -p /var/www/xenarch
cd /var/www/xenarch

# Create directories
mkdir -p uploads analysis_results logs
```

## 5. Clone and Configure the Application

```bash
# Install Git if not already installed
apt install -y git

# Clone the repository (use your own repository URL)
git clone https://github.com/yourusername/xenarch.git .
```

## 6. Set Up Backend

```bash
# Navigate to backend directory
cd /var/www/xenarch/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install gunicorn

# Create .env file (if needed)
cat > .env << EOF
FLASK_ENV=production
EOF

# Deactivate virtualenv
deactivate
```

## 7. Set Up Frontend

If using the React frontend:

```bash
# Install Node.js and npm if needed
apt install -y nodejs npm

# Navigate to frontend directory
cd /var/www/xenarch/frontend

# Install dependencies
npm install

# Build the app for production
npm run build
```

## 8. Configure Nginx

Create an Nginx configuration file:

```bash
cat > /etc/nginx/sites-available/xenarch << EOF
server {
    listen 80;
    server_name your_domain_or_ip;

    # Frontend files
    location / {
        root /var/www/xenarch/frontend/build;  # or /var/www/xenarch/frontend if using static HTML/JS
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Large file upload configuration
    client_max_body_size 32M;
}
EOF

# Enable the site
ln -s /etc/nginx/sites-available/xenarch /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default  # Remove default site if exists

# Test nginx configuration
nginx -t

# Restart nginx
systemctl restart nginx
```

## 9. Configure Supervisor for the Backend

Create a supervisor configuration to keep the backend running:

```bash
cat > /etc/supervisor/conf.d/xenarch.conf << EOF
[program:xenarch]
directory=/var/www/xenarch/backend
command=/var/www/xenarch/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 app:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/www/xenarch/logs/gunicorn.err.log
stdout_logfile=/var/www/xenarch/logs/gunicorn.out.log
EOF

# Update supervisor
supervisorctl reread
supervisorctl update
```

## 10. Set Permissions

```bash
# Set ownership of the application directory
chown -R www-data:www-data /var/www/xenarch

# Make sure log and data directories are writable
chmod -R 755 /var/www/xenarch
chmod -R 777 /var/www/xenarch/uploads
chmod -R 777 /var/www/xenarch/analysis_results
chmod -R 777 /var/www/xenarch/logs
```

## 11. Configure Firewall (Optional)

```bash
# Allow SSH, HTTP, and HTTPS
ufw allow ssh
ufw allow http
ufw allow https

# Enable firewall
ufw enable
```

## 12. SSL Configuration (Optional but Recommended)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Obtain and configure SSL certificate
certbot --nginx -d your_domain.com
```

## 13. Verify Deployment

1. Visit `http://your_domain_or_ip/` to access the frontend
2. Test API with `curl http://your_domain_or_ip/api/health`

## 14. Monitoring and Maintenance

- Check logs in `/var/www/xenarch/logs/`
- Restart services if needed:
  ```bash
  supervisorctl restart xenarch
  systemctl restart nginx
  ```
- Update application:
  ```bash
  cd /var/www/xenarch
  git pull
  cd backend
  source venv/bin/activate
  pip install -r requirements.txt
  supervisorctl restart xenarch
  ``` 