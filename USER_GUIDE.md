# 🚀 Face Detection Audit System - Complete Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation & Setup](#installation--setup)
4. [Using the Web Interface](#using-the-web-interface)
5. [API Documentation](#api-documentation)
6. [Deployment Options](#deployment-options)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This system converts your local Jupyter notebook face detection script into a **production-ready web application** with:

- ✅ **Beautiful Web Interface** - Modern, responsive UI
- ✅ **Real-time Progress** - Live updates during processing
- ✅ **Batch Processing** - Handle large CSV files efficiently
- ✅ **Multi-threading** - Fast parallel processing
- ✅ **Dual Detection** - MediaPipe + OpenCV DNN fallback
- ✅ **Easy Downloads** - Get results and images instantly

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     WEB BROWSER                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Modern UI (HTML/CSS/JavaScript)                   │     │
│  │  - File Upload                                     │     │
│  │  - Progress Tracking                               │     │
│  │  - Results Display                                 │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                   FLASK BACKEND (app.py)                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  API Endpoints                                     │     │
│  │  - /api/upload      - Upload CSV                   │     │
│  │  - /api/status      - Check progress               │     │
│  │  - /api/download    - Get results                  │     │
│  └────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Processing Engine (Multi-threaded)                │     │
│  │  - Download images from URLs                       │     │
│  │  - Face detection (MediaPipe + OpenCV)             │     │
│  │  - Save results and images                         │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   FILE SYSTEM                                │
│  - uploads/          (CSV files)                             │
│  - results/          (Processed CSV)                         │
│  - no_face_images/   (Images without faces)                  │
│  - Model/            (AI models)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Installation & Setup

### Step 1: Install Dependencies

```bash
cd "e:\My University Project\Project 2\face-audit-api"
pip install -r requirements.txt
```

### Step 2: Verify Model Files

Ensure these files exist in the `Model/` folder:
- ✅ `deploy.prototxt.txt`
- ✅ `res10_300x300_ssd_iter_140000.caffemodel`

### Step 3: Run the Server

```bash
python app.py
```

You should see:
```
🚀 Face Detection API Server Starting...
📁 Upload folder: uploads
📁 Results folder: results
📁 No Face folder: no_face_images
🤖 Models loaded successfully
🌐 Server running on http://localhost:5000
```

### Step 4: Access the Web Interface

Open your browser and go to:
- **Local**: http://localhost:5000
- **Network**: http://192.168.0.17:5000 (or your IP)

---

## 🖥️ Using the Web Interface

### 1. Upload CSV File

1. Click **"Browse Files"** or drag & drop your CSV file
2. Your CSV must have a column named **"Check-In Photo"** with image URLs
3. Click **"Start Processing"**

### 2. Monitor Progress

Watch real-time updates:
- **Progress bar** - Visual progress indicator
- **Statistics** - Good faces, no faces, errors
- **Percentage** - Completion percentage

### 3. Download Results

When complete, download:
- **Processed CSV** - Original CSV + Face_Status column
- **No-Face Images ZIP** - All images without detected faces

### 4. View History

See all your processing jobs in the **Recent Jobs** section.

---

## 📡 API Documentation

### Upload CSV
```http
POST /api/upload
Content-Type: multipart/form-data

Body: file=<csv_file>

Response:
{
  "job_id": "uuid-string",
  "message": "File uploaded successfully. Processing started."
}
```

### Check Status
```http
GET /api/status/<job_id>

Response:
{
  "id": "uuid-string",
  "status": "processing",
  "progress": 45.5,
  "total_rows": 1000,
  "processed": 455,
  "good_count": 400,
  "noface_count": 50,
  "download_error_count": 5
}
```

### Download Results CSV
```http
GET /api/download/<job_id>

Response: CSV file download
```

### Download No-Face Images
```http
GET /api/download-noface/<job_id>

Response: ZIP file download
```

### List All Jobs
```http
GET /api/jobs

Response:
[
  {
    "id": "uuid",
    "status": "completed",
    "original_filename": "data.csv",
    ...
  }
]
```

---

## 🌐 Deployment Options

### Option 1: Local Network (Current Setup)
- Already accessible on your local network
- URL: `http://<your-ip>:5000`
- Perfect for team use within the same network

### Option 2: Cloud Deployment (Heroku)

1. **Install Heroku CLI**
2. **Create Procfile**:
   ```
   web: gunicorn app:app
   ```
3. **Deploy**:
   ```bash
   heroku create face-detection-audit
   git push heroku main
   ```

### Option 3: Cloud Deployment (AWS/Google Cloud)

1. **Package application**
2. **Set up virtual machine**
3. **Install dependencies**
4. **Use Nginx + Gunicorn**

### Option 4: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t face-detection .
docker run -p 5000:5000 face-detection
```

---

## 🔧 Configuration Options

Edit `app.py` to customize:

```python
# Processing Configuration
DOWNLOAD_TIMEOUT = 20         # Image download timeout (seconds)
MEDIAPIPE_CONF_THRESH = 0.80  # MediaPipe confidence (0.0-1.0)
DNN_CONF_THRESH = 0.70        # OpenCV DNN confidence (0.0-1.0)
NUM_THREADS = 6               # Parallel processing threads
BATCH_SIZE = 100              # Rows per batch

# Server Configuration
app.run(
    debug=True,              # Set to False in production
    host='0.0.0.0',          # Listen on all interfaces
    port=5000                # Change if port is busy
)
```

---

## 🐛 Troubleshooting

### Issue: Port 5000 Already in Use

**Solution**: Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Model Files Not Found

**Error**: `FileNotFoundError: Model files not found`

**Solution**: 
1. Check `Model/` folder exists
2. Verify both files are present:
   - `deploy.prototxt.txt`
   - `res10_300x300_ssd_iter_140000.caffemodel`

### Issue: Memory Error During Processing

**Solution**: Reduce resource usage:
```python
NUM_THREADS = 3      # Reduce threads
BATCH_SIZE = 50      # Smaller batches
```

### Issue: Images Not Downloading

**Possible causes**:
- Network connectivity
- Invalid URLs
- Firewall blocking requests

**Solution**: Check the CSV and increase timeout:
```python
DOWNLOAD_TIMEOUT = 30
```

### Issue: Face Detection Too Sensitive/Not Sensitive

**Solution**: Adjust confidence thresholds:
```python
# More strict (fewer false positives)
MEDIAPIPE_CONF_THRESH = 0.90
DNN_CONF_THRESH = 0.80

# More lenient (catch more faces)
MEDIAPIPE_CONF_THRESH = 0.70
DNN_CONF_THRESH = 0.60
```

---

## 📊 Performance Tips

1. **Optimize Thread Count**: Match your CPU cores
   ```python
   import os
   NUM_THREADS = os.cpu_count()
   ```

2. **Batch Size**: Balance memory vs. progress updates
   - Large batches = faster, less frequent updates
   - Small batches = slower, more frequent updates

3. **Network Speed**: Ensure good internet for image downloads

4. **CSV Size**: For very large files (>10,000 rows), consider:
   - Splitting into multiple files
   - Increasing batch size
   - Running overnight

---

## 🎨 Customization

### Change Colors

Edit `static/style.css`:
```css
:root {
    --primary: hsl(240, 100%, 65%);  /* Main color */
    --success: hsl(142, 71%, 45%);   /* Success color */
    --danger: hsl(0, 84%, 60%);      /* Error color */
}
```

### Add Logo

Replace the SVG in `static/index.html`:
```html
<div class="logo">
    <img src="your-logo.png" alt="Logo">
    <h1>Your Company Name</h1>
</div>
```

---

## 📈 Monitoring

Check server logs for:
- Upload events
- Processing progress
- Errors and warnings

Example log output:
```
🚀 Starting Batch 1/5 (Size: 100)
✅ Batch 1 Summary (Processed 100 rows)
Batch GOOD Faces        : 85
Batch NO FACE Images    : 12
Batch DOWNLOAD FAILURES : 3
```

---

## 🔒 Security Considerations

For production deployment:

1. **Disable Debug Mode**:
   ```python
   app.run(debug=False)
   ```

2. **Add Authentication**: Use Flask-Login or JWT

3. **File Size Limits**: Add max file size validation

4. **Rate Limiting**: Prevent abuse with Flask-Limiter

5. **HTTPS**: Use SSL certificates in production

---

## 📞 Support

For issues or questions:
1. Check this guide
2. Review error logs
3. Verify CSV format
4. Test with sample data

---

**Happy Face Detecting! 🎯**
