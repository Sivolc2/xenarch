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

## 3. Install Python 3.12

```bash
# Update package lists
apt update
apt install -y software-properties-common

# Add deadsnakes PPA for Python 3.12
add-apt-repository -y ppa:deadsnakes/ppa
apt update

# Install Python 3.12 and required packages
apt install -y python3.12 python3.12-venv python3.12-dev python3.12-distutils

# Verify installation
python3.12 --version
```

## 4. Install System Dependencies

```bash
# Install system dependencies
apt install -y nginx supervisor

# Install GDAL dependencies
apt install -y gdal-bin libgdal-dev

# Install build essentials and scientific computing dependencies
apt install -y build-essential libatlas-base-dev gfortran

# Install Python Pip for Python 3.12
apt install -y curl
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
```

## 5. Set Up Project Structure

```bash
# Create application directory
mkdir -p /var/www/xenarch
cd /var/www/xenarch

# Create directories
mkdir -p uploads analysis_results logs
```

## 6. Clone and Configure the Application

```bash
# Install Git if not already installed
apt install -y git

# Clone the repository (use your own repository URL)
git clone https://github.com/yourusername/xenarch.git .
```

## 7. Set Up Backend with Python 3.12

```bash
# Navigate to backend directory
cd /var/www/xenarch/backend

# Create and activate virtual environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate

# Verify the Python version in the virtual environment
python --version  # Should show Python 3.12.x

# Ensure pip, setuptools, and wheel are up-to-date
pip install --upgrade pip setuptools wheel

# Install Python dependencies
pip install -r requirements.txt

# Create .env file for production
cat > .env << EOF
FLASK_ENV=production
HOST=127.0.0.1
PORT=5001
ALLOWED_ORIGINS=*
EOF

# Deactivate virtualenv
deactivate
```

### 7.1 Troubleshooting GDAL/Rasterio Installation

If you encounter issues with the rasterio package:

```bash
source venv/bin/activate

# Set GDAL configuration and install rasterio
export GDAL_CONFIG=/usr/bin/gdal-config
pip install --no-binary :all: rasterio

# If scipy has issues:
pip install --no-binary :all: scipy

# Exit virtual environment
deactivate
```

## 8. Set Up Frontend

### 8.1 For Production (Build Static Files)

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

### 8.2 For Development Mode (Run Development Server)

If you want to run the frontend in development mode on the server:

```bash
# Install Node.js and npm if needed (if not done already)
apt install -y nodejs npm

# Navigate to frontend directory
cd /var/www/xenarch/frontend

# Install dependencies (if not done already)
npm install

# Create a development environment file
cat > .env.development << EOF
HOST=0.0.0.0
PORT=3000
BROWSER=none
WDS_SOCKET_HOST=0.0.0.0
DANGEROUSLY_DISABLE_HOST_CHECK=true
CHOKIDAR_USEPOLLING=true
EOF

# Start the development server (this will keep running in the terminal)
npm run start

# To run in the background:
# nohup npm run start > frontend.log 2>&1 &
```

When running in development mode, open your firewall to allow access to port 3000:

```bash
ufw allow 3000/tcp
```

## 9. Configure Nginx

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
        
        # Increase timeouts for long-running operations
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
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

## 10. Configure Supervisor for the Backend with Python 3.12

Create a supervisor configuration to keep the backend running:

```bash
cat > /etc/supervisor/conf.d/xenarch.conf << EOF
[program:xenarch]
directory=/var/www/xenarch/backend
command=/var/www/xenarch/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 app:app --timeout 300
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

## 11. Set Permissions

```bash
# Set ownership of the application directory
chown -R www-data:www-data /var/www/xenarch

# Make sure log and data directories are writable
chmod -R 755 /var/www/xenarch
chmod -R 777 /var/www/xenarch/uploads
chmod -R 777 /var/www/xenarch/analysis_results
chmod -R 777 /var/www/xenarch/logs
```

## 12. Configure Firewall (Optional)

```bash
# Allow SSH, HTTP, and HTTPS
ufw allow ssh
ufw allow http
ufw allow https

# Enable firewall
ufw enable
```

## 13. SSL Configuration (Optional but Recommended)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Obtain and configure SSL certificate
certbot --nginx -d your_domain.com
```

## 14. Verify Deployment

1. Visit `http://your_domain_or_ip/` to access the frontend
2. Test API with `curl http://your_domain_or_ip/api/health`

## 15. Monitoring and Maintenance

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

## 16. Automated Setup with Script

For a streamlined setup, you can use the included setup script:

```bash
# Navigate to the project directory
cd /var/www/xenarch

# Make the setup script executable
chmod +x backend/scripts/setup_py312.sh

# Run the setup script (it will handle Python 3.12 installation)
sudo backend/scripts/setup_py312.sh
``` 