# 🌐 Deployment Guide - Making Your App Online

This guide shows you how to deploy your Face Detection Audit System to the internet so it's accessible from anywhere.

---

## 🎯 Deployment Options Comparison

| Option | Cost | Difficulty | Best For |
|--------|------|------------|----------|
| **Render** | Free tier available | ⭐ Easy | Quick deployment, testing |
| **Railway** | Free tier available | ⭐ Easy | Modern deployment |
| **Heroku** | $5-7/month | ⭐⭐ Medium | Production apps |
| **PythonAnywhere** | Free tier available | ⭐ Easy | Python apps |
| **AWS/GCP** | Pay-as-you-go | ⭐⭐⭐ Hard | Enterprise |
| **DigitalOcean** | $5/month | ⭐⭐ Medium | Full control |

---

## 🚀 Option 1: Render (Recommended - FREE)

### Why Render?
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Easy setup
- ✅ HTTPS included

### Steps:

1. **Create a GitHub Repository**
   ```bash
   cd "e:\My University Project\Project 2\face-audit-api"
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/face-audit-api.git
   git push -u origin main
   ```

2. **Create `render.yaml`** (in project root):
   ```yaml
   services:
     - type: web
       name: face-detection-audit
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn app:app
       envVars:
         - key: PYTHON_VERSION
           value: 3.10.0
   ```

3. **Update `requirements.txt`** (add gunicorn):
   ```txt
   flask>=3.0.0
   flask-cors>=4.0.0
   pandas>=2.0.0
   requests>=2.31.0
   opencv-python-headless>=4.8.0
   mediapipe>=0.10.0
   numpy>=1.24.0
   tqdm>=4.66.0
   gunicorn>=21.0.0
   ```

4. **Sign up at [render.com](https://render.com)**

5. **Create New Web Service**:
   - Connect your GitHub repository
   - Select the repository
   - Render will auto-detect Python
   - Click "Create Web Service"

6. **Wait for deployment** (5-10 minutes)

7. **Access your app** at: `https://your-app-name.onrender.com`

---

## 🚂 Option 2: Railway (FREE)

### Steps:

1. **Create `Procfile`**:
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT
   ```

2. **Create `runtime.txt`**:
   ```
   python-3.10.0
   ```

3. **Sign up at [railway.app](https://railway.app)**

4. **Deploy**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway auto-deploys!

5. **Access**: Railway provides a URL automatically

---

## 🟣 Option 3: Heroku

### Steps:

1. **Install Heroku CLI**:
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create `Procfile`**:
   ```
   web: gunicorn app:app
   ```

3. **Create `runtime.txt`**:
   ```
   python-3.10.13
   ```

4. **Update requirements.txt** (add gunicorn):
   ```bash
   echo "gunicorn>=21.0.0" >> requirements.txt
   ```

5. **Deploy**:
   ```bash
   heroku login
   heroku create face-detection-audit
   git push heroku main
   heroku open
   ```

---

## 🐍 Option 4: PythonAnywhere (FREE)

### Steps:

1. **Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)**

2. **Upload your files**:
   - Use the Files tab to upload your project
   - Or clone from GitHub

3. **Create a virtual environment**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 myenv
   pip install -r requirements.txt
   ```

4. **Configure Web App**:
   - Go to Web tab
   - Add new web app
   - Select Flask
   - Point to your `app.py`

5. **Set WSGI configuration**:
   ```python
   import sys
   path = '/home/yourusername/face-audit-api'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```

6. **Reload** and access at: `yourusername.pythonanywhere.com`

---

## ☁️ Option 5: DigitalOcean (Full Control)

### Steps:

1. **Create Droplet** (Ubuntu 22.04, $5/month)

2. **SSH into server**:
   ```bash
   ssh root@your-server-ip
   ```

3. **Install dependencies**:
   ```bash
   apt update
   apt install python3-pip python3-venv nginx
   ```

4. **Upload your code**:
   ```bash
   git clone https://github.com/yourusername/face-audit-api.git
   cd face-audit-api
   ```

5. **Set up virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

6. **Create systemd service** (`/etc/systemd/system/faceaudit.service`):
   ```ini
   [Unit]
   Description=Face Detection Audit
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/root/face-audit-api
   Environment="PATH=/root/face-audit-api/venv/bin"
   ExecStart=/root/face-audit-api/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

   [Install]
   WantedBy=multi-user.target
   ```

7. **Start service**:
   ```bash
   systemctl start faceaudit
   systemctl enable faceaudit
   ```

8. **Configure Nginx** (`/etc/nginx/sites-available/faceaudit`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

9. **Enable site**:
   ```bash
   ln -s /etc/nginx/sites-available/faceaudit /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

10. **Add SSL (optional)**:
    ```bash
    apt install certbot python3-certbot-nginx
    certbot --nginx -d your-domain.com
    ```

---

## 🔧 Important Changes for Production

### 1. Update `app.py` for Production

```python
# Change this line:
app.run(debug=True, host='0.0.0.0', port=5000)

# To this:
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
```

### 2. Use opencv-python-headless

In `requirements.txt`, change:
```txt
opencv-python>=4.8.0
```
To:
```txt
opencv-python-headless>=4.8.0
```

This version works better on servers without GUI.

### 3. Add Environment Variables

Create `.env` file (don't commit this):
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
MAX_UPLOAD_SIZE=104857600
```

Update `app.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 104857600))
```

---

## 📊 Monitoring Your Deployed App

### Add Health Check Endpoint

Add to `app.py`:
```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
```

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in your code:
logger.info(f"Processing job {job_id}")
logger.error(f"Error processing: {str(e)}")
```

---

## 🔒 Security Checklist

Before going live:

- [ ] Set `debug=False` in production
- [ ] Add file size limits
- [ ] Implement rate limiting
- [ ] Add authentication (if needed)
- [ ] Use HTTPS
- [ ] Set up CORS properly
- [ ] Validate file uploads
- [ ] Add error handling
- [ ] Set up logging
- [ ] Regular backups

---

## 💰 Cost Estimates

### Free Tiers:
- **Render**: 750 hours/month free
- **Railway**: $5 credit/month
- **PythonAnywhere**: Limited free tier
- **Heroku**: No longer has free tier

### Paid Options:
- **Heroku**: ~$7/month (Eco dyno)
- **DigitalOcean**: $5/month (basic droplet)
- **AWS**: ~$10-20/month (t2.micro)

---

## 🎯 Recommended Path

For your use case, I recommend:

1. **Start with Render (Free)** - Perfect for testing and demos
2. **Move to Railway** - If you need more resources
3. **Upgrade to DigitalOcean** - For production with full control

---

## 🚀 Quick Deploy Commands

### For Render/Railway/Heroku:

```bash
# 1. Initialize git
git init
git add .
git commit -m "Initial commit"

# 2. Create GitHub repo and push
git remote add origin https://github.com/yourusername/face-audit-api.git
git push -u origin main

# 3. Connect to Render/Railway/Heroku via their dashboard
# They'll auto-deploy from GitHub!
```

---

## 📞 Need Help?

Common deployment issues:

1. **Build fails**: Check Python version compatibility
2. **App crashes**: Check logs in deployment platform
3. **Slow performance**: Upgrade to paid tier or optimize code
4. **Out of memory**: Reduce batch size and threads

---

**Ready to go online! 🌐**

Choose your deployment platform and follow the steps above. Your face detection system will be accessible worldwide in minutes!
