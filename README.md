# Face Detection Audit System 🎯

A modern web-based face detection system that processes CSV files containing image URLs and identifies whether images contain faces using MediaPipe and OpenCV DNN models.

## ✨ Features

- **📤 CSV Upload**: Upload CSV files with image URLs
- **🤖 Dual Detection**: Uses MediaPipe + OpenCV DNN for accurate face detection
- **📊 Real-time Progress**: Live progress tracking with detailed statistics
- **💾 Results Download**: Download processed CSV and no-face images
- **🎨 Modern UI**: Beautiful, responsive interface with animations
- **⚡ Fast Processing**: Multi-threaded processing for speed
- **📱 Mobile Friendly**: Fully responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "e:\My University Project\Project 2\face-audit-api"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure Model files are in place**
   
   Make sure the `Model` folder contains:
   - `deploy.prototxt.txt`
   - `res10_300x300_ssd_iter_140000.caffemodel`

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   
   Navigate to: `http://localhost:5000`

## 📋 CSV File Format

Your CSV file should contain a column named **"Check-In Photo"** with image URLs:

```csv
id,Check-In Photo,Other Columns...
1,https://example.com/image1.jpg,...
2,https://example.com/image2.jpg,...
```

The system will add a **"Face_Status"** column with one of these values:
- `GOOD` - Face detected successfully
- `NO FACE` - No face detected (image saved for manual review)
- `DOWNLOAD_ERROR` - Failed to download image
- `SYSTEM_ERROR` - Processing error

## 🎯 How It Works

1. **Upload**: Upload your CSV file through the web interface
2. **Processing**: The system:
   - Downloads images from URLs
   - Detects faces using MediaPipe (primary)
   - Falls back to OpenCV DNN if needed
   - Saves images without faces for manual review
3. **Results**: Download:
   - Processed CSV with face detection results
   - ZIP file of images without faces

## 🛠️ Configuration

Edit `app.py` to customize:

```python
DOWNLOAD_TIMEOUT = 20         # Image download timeout (seconds)
MEDIAPIPE_CONF_THRESH = 0.80  # MediaPipe confidence threshold
DNN_CONF_THRESH = 0.70        # OpenCV DNN confidence threshold
NUM_THREADS = 6               # Number of processing threads
BATCH_SIZE = 100              # Batch size for processing
```

## 📁 Project Structure

```
face-audit-api/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── Model/                 # Face detection models
│   ├── deploy.prototxt.txt
│   └── res10_300x300_ssd_iter_140000.caffemodel
├── static/               # Frontend files
│   ├── index.html        # Main page
│   ├── style.css         # Styling
│   └── script.js         # Client-side logic
├── uploads/              # Uploaded CSV files (auto-created)
├── results/              # Processed CSV files (auto-created)
└── no_face_images/       # Images without faces (auto-created)
```

## 🌐 API Endpoints

- `POST /api/upload` - Upload CSV file
- `GET /api/status/<job_id>` - Get job status
- `GET /api/download/<job_id>` - Download processed CSV
- `GET /api/download-noface/<job_id>` - Download no-face images ZIP
- `GET /api/jobs` - List all jobs

## 🔧 Troubleshooting

### Port Already in Use
If port 5000 is busy, change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Model Files Not Found
Ensure the Model folder contains both required files:
- `deploy.prototxt.txt`
- `res10_300x300_ssd_iter_140000.caffemodel`

### Memory Issues
Reduce batch size and thread count in `app.py`:
```python
NUM_THREADS = 3
BATCH_SIZE = 50
```

## 🚀 Deployment

### Local Network Access
The app runs on `0.0.0.0`, making it accessible on your local network:
```
http://<your-ip-address>:5000
```

### Production Deployment
For production, consider:
- Using **Gunicorn** or **uWSGI** instead of Flask's dev server
- Setting up **Nginx** as a reverse proxy
- Using **Redis** for job queue management
- Deploying to **Heroku**, **AWS**, **Google Cloud**, or **Azure**

## 📝 License

This project is for educational/internal use.

## 🙏 Credits

- **MediaPipe** - Google's ML framework
- **OpenCV** - Computer vision library
- **Flask** - Python web framework

---

**Made with ❤️ for efficient face detection auditing**
