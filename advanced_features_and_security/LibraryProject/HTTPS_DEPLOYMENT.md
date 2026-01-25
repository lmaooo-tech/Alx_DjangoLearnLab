# HTTPS Deployment Configuration Guide

## Overview
This guide provides instructions for configuring your LibraryProject Django application to run securely over HTTPS. It includes setup for popular web servers (Nginx and Apache) and SSL/TLS certificate management.

## Prerequisites
- A registered domain name
- SSL/TLS certificate (from Let's Encrypt, DigiCert, etc.)
- Web server (Nginx or Apache)
- Python virtual environment with Django installed

## Step 1: Obtain SSL/TLS Certificates

### Option A: Using Let's Encrypt (Recommended - Free)

1. Install Certbot:
```bash
sudo apt-get update
sudo apt-get install certbot
```

2. For Nginx:
```bash
sudo apt-get install python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

3. For Apache:
```bash
sudo apt-get install python3-certbot-apache
sudo certbot certonly --apache -d yourdomain.com -d www.yourdomain.com
```

4. Auto-renewal:
```bash
sudo certbot renew --dry-run
```

### Option B: Using Purchased Certificates
- Follow your certificate provider's instructions
- Store certificates in a secure location (e.g., `/etc/ssl/certs/`)

## Step 2: Configure Django Settings

The application settings have been preconfigured with the following HTTPS-related settings:

### Environment Variables for Production

Create a `.env` file or set environment variables:

```bash
# Enable HTTPS redirect (set to 'true' in production)
SECURE_SSL_REDIRECT=true

# HSTS settings
SECURE_HSTS_SECONDS=31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS=true
SECURE_HSTS_PRELOAD=true

# Secret key (use a strong, random value)
DJANGO_SECRET_KEY=your-very-secure-random-key-here

# Debug mode
DJANGO_DEBUG=false

# Allowed hosts
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Trusted origins for CSRF
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Step 3: Configure Nginx

Create or update `/etc/nginx/sites-available/libraryproject`:

```nginx
# HTTP redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS server block
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificate Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Protocol and Ciphers (strong security)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HSTS Header (enforced by Django as well)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

    # Additional Security Headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Session timeout
    client_body_timeout 12;
    client_header_timeout 12;
    keepalive_timeout 15;
    send_timeout 10;

    # Proxy settings for Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Static files
    location /static/ {
        alias /path/to/libraryproject/staticfiles/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /path/to/libraryproject/media/;
        expires 7d;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/libraryproject /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

## Step 4: Configure Apache

Create or update `/etc/apache2/sites-available/libraryproject-ssl.conf`:

```apache
# HTTP to HTTPS redirect
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    RewriteEngine On
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</VirtualHost>

# HTTPS configuration
<VirtualHost *:443>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/yourdomain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/yourdomain.com/privkey.pem
    
    # SSL Protocol Configuration
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    SSLCipherSuite HIGH:!aNULL:!MD5
    SSLHonorCipherOrder on

    # HSTS Header
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"

    # Security Headers
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "DENY"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"

    # Proxy settings for Django
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/

    # Set headers for proxied requests
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-For "%{REMOTE_ADDR}s"

    # Static and Media files
    Alias /static/ /path/to/libraryproject/staticfiles/
    Alias /media/ /path/to/libraryproject/media/

    <Directory /path/to/libraryproject/staticfiles/>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 30 days"
    </Directory>

    <Directory /path/to/libraryproject/media/>
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 7 days"
    </Directory>
</VirtualHost>
```

Enable the site:
```bash
sudo a2enmod ssl rewrite headers proxy proxy_http
sudo a2ensite libraryproject-ssl.conf
sudo apache2ctl configtest  # Should show "Syntax OK"
sudo systemctl restart apache2
```

## Step 5: Django Application Setup

1. Collect static files:
```bash
python manage.py collectstatic --noinput
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start Gunicorn (recommended for production):
```bash
gunicorn LibraryProject.wsgi:application --bind 127.0.0.1:8000 --workers 4
```

## Step 6: Security Verification

Test your HTTPS configuration:

1. SSL Labs Test:
   - Visit https://www.ssllabs.com/ssltest/
   - Enter your domain
   - Verify you get an "A" or "A+" rating

2. Check Security Headers:
   - Visit https://securityheaders.com
   - Enter your domain
   - Verify all security headers are present

3. Test HSTS:
   ```bash
   curl -i https://yourdomain.com
   # Should show: Strict-Transport-Security header
   ```

## Step 7: Monitoring and Maintenance

### Certificate Renewal Automation
```bash
# For Let's Encrypt with auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Log Monitoring
```bash
# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Apache logs
sudo tail -f /var/log/apache2/access.log
sudo tail -f /var/log/apache2/error.log
```

## Troubleshooting

### HTTPS Redirect Loop
- Check that your proxy headers are correctly configured
- Ensure `X-Forwarded-Proto` is set to `https`

### Certificate Not Found
- Verify certificate paths in web server config
- Check file permissions: `sudo ls -la /etc/letsencrypt/live/`

### Mixed Content Warnings
- Ensure all resources (CSS, JS, images) are served over HTTPS
- Use protocol-relative URLs: `//example.com/resource`

### CSRF Token Errors
- Verify `DJANGO_CSRF_TRUSTED_ORIGINS` includes your domain
- Check that `CSRF_COOKIE_SECURE` is `True`

## Summary

Your Django application is now configured to:
- ✅ Enforce HTTPS connections
- ✅ Prevent SSL downgrade attacks with HSTS
- ✅ Use secure cookies (session and CSRF)
- ✅ Implement security headers against common attacks
- ✅ Serve static and media files securely
- ✅ Auto-renew SSL certificates

For more information, refer to:
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
