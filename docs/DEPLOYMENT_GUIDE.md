# Shogi Bot AI - Deployment Guide

## Local Development Setup

### Prerequisites

- Python 3.11+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Git (for cloning the repository)

### Installation Steps

1. **Clone the repository:**
```bash
git clone <repository-url>
cd shogi-bot-ai
```

2. **Install Python dependencies:**
```bash
cd backend
pip3 install -r requirements.txt
```

3. **Start the backend server:**
```bash
python3 -m backend.run
```
The server will start on `http://localhost:5000`

4. **Open the frontend:**
Open `frontend/index.html` in your web browser, or serve it via a local HTTP server:
```bash
cd frontend
python3 -m http.server 8080
```
Then visit `http://localhost:8080`

## Production Deployment

### Backend Deployment Options

#### Option 1: Using Gunicorn (Recommended)

1. **Install Gunicorn:**
```bash
pip3 install gunicorn
```

2. **Create a WSGI entry point (`wsgi.py`):**
```python
from backend.app import app

if __name__ == "__main__":
    app.run()
```

3. **Run with Gunicorn:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

#### Option 2: Using Docker

1. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python3", "-m", "backend.run"]
```

2. **Build and run:**
```bash
docker build -t shogi-bot-ai .
docker run -p 5000:5000 shogi-bot-ai
```

### Frontend Deployment Options

#### Option 1: Static File Hosting

Upload the `frontend/` directory to any static file hosting service:
- GitHub Pages
- Netlify
- Vercel
- AWS S3 + CloudFront
- Firebase Hosting

#### Option 2: Web Server

Serve the frontend files using a web server like Nginx or Apache:

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/shogi-bot-ai/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Configuration

#### Backend Environment Variables

Create a `.env` file in the backend directory:
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
```

#### Frontend Configuration

Update the API base URL in `frontend/js/api.js`:
```javascript
class ShogiAPI {
    constructor(baseURL = 'https://your-api-domain.com') {
        this.baseURL = baseURL;
    }
    // ...
}
```

### Security Considerations

1. **HTTPS**: Always use HTTPS in production
2. **CORS**: Configure CORS properly for your domain
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Input Validation**: Ensure all inputs are validated
5. **Secret Keys**: Use strong, unique secret keys

### Performance Optimization

#### Backend Optimizations

1. **Caching**: Implement Redis for game state caching
2. **Database**: Consider using a database for persistent storage
3. **Load Balancing**: Use multiple backend instances behind a load balancer

#### Frontend Optimizations

1. **Minification**: Minify CSS and JavaScript files
2. **Compression**: Enable gzip compression
3. **CDN**: Use a CDN for static assets
4. **Caching**: Implement proper browser caching headers

### Monitoring and Logging

#### Backend Logging

Add logging configuration to `backend/app.py`:
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/shogi-bot.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

#### Health Checks

The API includes a health check endpoint at `/api/health` for monitoring.

### Scaling Considerations

1. **Horizontal Scaling**: Deploy multiple backend instances
2. **Database**: Use a shared database for game state
3. **Session Management**: Implement proper session management
4. **WebSocket**: Consider WebSocket for real-time updates

### Troubleshooting

#### Common Issues

1. **CORS Errors**: Ensure CORS is properly configured
2. **Port Conflicts**: Check if ports 5000/8080 are available
3. **Python Path**: Ensure Python modules can be imported correctly
4. **File Permissions**: Check file permissions for static files

#### Debug Mode

Enable debug mode for development:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Backup and Recovery

1. **Game Data**: Implement game state persistence
2. **Configuration**: Backup configuration files
3. **Logs**: Implement log rotation and archival
4. **Database**: Regular database backups if using persistent storage

## Cloud Deployment Examples

### AWS Deployment

1. **EC2**: Deploy on EC2 instances with Auto Scaling
2. **ELB**: Use Elastic Load Balancer for high availability
3. **RDS**: Use RDS for database if needed
4. **S3**: Host frontend on S3 with CloudFront

### Google Cloud Platform

1. **App Engine**: Deploy backend on App Engine
2. **Cloud Storage**: Host frontend on Cloud Storage
3. **Cloud SQL**: Use Cloud SQL for database
4. **Load Balancer**: Use Cloud Load Balancing

### Heroku Deployment

1. **Create Procfile:**
```
web: gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

2. **Deploy:**
```bash
heroku create shogi-bot-ai
git push heroku main
```

This deployment guide provides comprehensive instructions for both development and production environments, ensuring the Shogi Bot AI can be successfully deployed in various scenarios.

