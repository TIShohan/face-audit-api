# 🔍 Face Detection Audit API

A robust, production-ready SaaS tool for auditing large datasets of user images. It detects faces using a Dual-Engine approach and generates detailed CSV reports indicating which images have valid faces and which do not.

![Face Audit Interface](static/images/hero_placeholder.png)

## 🚀 Key Features

- **Dual AI Engine**: Uses **MediaPipe (Google)** for speed/accuracy + **OpenCV DNN** as a robust fallback.
- **Massive Scale**: Capable of processing **50,000+ rows** without crashing.
- **Smart Streaming**: Downloads result ZIPs (even 10GB+) using a streaming generator to prevent memory overflows.
- **Crash Proof**: "Session Restore" feature remembers your job if you accidentally close the tab.
- **Advanced Config**: Tweak sensitivity thresholds, thread counts, and download timeouts per job.
- **No-Storage Mode**: Option to process without saving "No Face" images (Faster / Zero Disk Usage).

## �️ Tech Stack

- **Backend**: Python 3.12, Flask, Gunicorn, APScheduler (Auto-cleanup).
- **Frontend**: HTML5, Vanilla JS, CSS (Responsive).
- **AI/ML**: MediaPipe, OpenCV, NumPy.

## 🏁 Quick Start (Local)

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/face-audit-api.git
   cd face-audit-api
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the App**
   ```bash
   python app.py
   ```
   Open `http://localhost:5000` in your browser.

## ☁️ Deployment

This app is optimized for **Render**, **Railway**, and **Heroku**.
It includes:
- `gunicorn` for production serving.
- `opencv-python-headless` for server compatibility.
- 100MB Upload Limits & Single-Worker safety config.

👉 **[Read the Full Deployment Guide](DEPLOYMENT.md)**

## ⚙️ Configuration Options

| Setting | Default | Description |
| :--- | :--- | :--- |
| **Download Timeout** | 20s | Max time to wait for an image URL. |
| **MediaPipe Thresh** | 0.80 | Confidence level to accept a face (0.0 - 1.0). |
| **DNN Thresh** | 0.70 | Confidence level for the fallback engine. |
| **Batch Size** | 50 | Update UI progress every X images. |
| **Save Images** | ON | if OFF, "No Face" images are discarded (Speed Mode). |

## �️ Privacy & Security

- **Auto-Cleanup**: The system automatically deletes all uploads and results older than **24 hours**.
- **Ephemeral**: On cloud platforms (Render), data is wiped on every restart.

## � License

MIT License. Free to use for personal or commercial projects.
