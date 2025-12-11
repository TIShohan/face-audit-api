# 🚀 Quick Reference Card

## 📍 Access URLs
- **Local**: http://localhost:5000
- **Network**: http://192.168.0.17:5000

## 🎮 Common Commands

### Start Server
```bash
cd "e:\My University Project\Project 2\face-audit-api"
python app.py
```

### Stop Server
Press `Ctrl+C` in the terminal

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Check Server Status
Visit: http://localhost:5000/health

## 📁 Important Files

| File | Purpose |
|------|---------|
| `app.py` | Main Flask server |
| `static/index.html` | Web interface |
| `static/style.css` | Styling |
| `static/script.js` | Client logic |
| `requirements.txt` | Dependencies |
| `sample_test.csv` | Test data |

## 📚 Documentation

| Document | What's Inside |
|----------|---------------|
| `README.md` | Quick start guide |
| `USER_GUIDE.md` | Complete usage manual |
| `DEPLOYMENT.md` | Deploy to cloud |
| `PROJECT_SUMMARY.md` | Full overview |

## 🔧 Configuration (in app.py)

```python
DOWNLOAD_TIMEOUT = 20         # Image download timeout
MEDIAPIPE_CONF_THRESH = 0.80  # Face detection confidence
DNN_CONF_THRESH = 0.70        # Backup detection confidence
NUM_THREADS = 6               # Processing threads
BATCH_SIZE = 100              # Batch size
```

## 📊 CSV Format Required

Your CSV must have a column named: **"Check-In Photo"**

Example:
```csv
id,Check-In Photo,Name
1,https://example.com/image1.jpg,John
2,https://example.com/image2.jpg,Jane
```

## 🎯 Face Detection Results

| Status | Meaning |
|--------|---------|
| `GOOD` | Face detected ✅ |
| `NO FACE` | No face found ❌ |
| `DOWNLOAD_ERROR` | Image download failed 🔴 |
| `SYSTEM_ERROR` | Processing error ⚠️ |

## 🌐 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Web interface |
| `/api/upload` | POST | Upload CSV |
| `/api/status/<id>` | GET | Check progress |
| `/api/download/<id>` | GET | Download CSV |
| `/api/download-noface/<id>` | GET | Download images |
| `/api/jobs` | GET | List all jobs |

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Port in use | Change port in `app.py` |
| Models not found | Check `Model/` folder |
| Memory error | Reduce threads/batch size |
| Slow processing | Increase threads |
| Can't access | Check firewall |

## 📱 Browser Compatibility

✅ Chrome, Edge, Firefox, Safari
✅ Mobile browsers
✅ Tablets

## 🎨 UI Features

- Drag & drop upload
- Real-time progress
- Live statistics
- Job history
- One-click downloads
- Responsive design

## 🚀 Deploy Options

| Platform | Cost | Difficulty |
|----------|------|------------|
| Render | Free | ⭐ Easy |
| Railway | Free | ⭐ Easy |
| Heroku | $7/mo | ⭐⭐ Medium |
| DigitalOcean | $5/mo | ⭐⭐ Medium |

## 💡 Pro Tips

1. **Test first**: Use `sample_test.csv`
2. **Check format**: Ensure "Check-In Photo" column exists
3. **Monitor**: Watch console for errors
4. **Adjust**: Tweak confidence thresholds as needed
5. **Backup**: Keep original CSV files

## 📞 Need Help?

1. Check `USER_GUIDE.md`
2. Review console logs
3. Test with sample data
4. Verify CSV format
5. Check internet connection

## ⚡ Performance Tips

- **Fast**: 6 threads, batch 100
- **Balanced**: 4 threads, batch 50
- **Safe**: 2 threads, batch 25

## 🎯 Success Checklist

- [ ] Server running
- [ ] Browser open
- [ ] CSV uploaded
- [ ] Processing complete
- [ ] Results downloaded
- [ ] Images reviewed

---

**Keep this card handy for quick reference!** 📌
