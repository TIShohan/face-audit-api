# 🚀 Absolute Beginner's Guide to Deployment

This guide will help you put your Face Audit App on the internet so anyone can use it. We will use **Render.com** because it is free, easy, and works perfectly with Python.

---

## ✅ Phase 1: Prepare Your Code (Do this on your PC)

Before we upload anything, we need to make sure your project is "Git Ready".

1.  **Open your project folder** in VS Code or File Explorer.
2.  **Right-click** inside the folder -> Select "Git Bash Here" (or open your Terminal).
3.  **Run these commands** one by one (copy and paste):

    ```bash
    # 1. Initialize Git (This turns your folder into a tracked repository)
    git init
    
    # 2. Add all your files to the staging area
    git add .
    
    # 3. Save these files as the first "version"
    git commit -m "Initial launch of Face Audit App"
    
    # 4. Rename the main branch to 'main' (Standard practice)
    git branch -M main
    ```

---

## ☁️ Phase 2: Create a GitHub Repository

We need to upload your code to GitHub first. Render will "read" your code from there.

1.  Go to **[github.com](https://github.com)** and Log In (or Sign Up).
2.  Click the **+** (plus icon) in the top right -> **New repository**.
3.  **Repository name**: `face-audit-api` (or any name you like).
4.  **Public/Private**: Choose **Public** (Easiest) or Private.
5.  Click the Green Button: **Create repository**.
6.  **Copy the URL** provided (it looks like `https://github.com/YourName/face-audit-api.git`).

7.  **Back in your Terminal (VS Code)**, run these commands:
    *(Replace the URL with YOUR copied URL)*

    ```bash
    # Link your computer to GitHub
    git remote add origin https://github.com/YourName/face-audit-api.git
    
    # Upload everything!
    git push -u origin main
    ```

---

## 🚀 Phase 3: Launch on Render.com

This is where the magic happens.

1.  Go to **[dashboard.render.com](https://dashboard.render.com)** and Log In (Use your GitHub account).
2.  Click the **"New +"** button -> Select **"Web Service"**.
3.  Technique: **"Build and deploy from a Git repository"**. Click Next.
4.  You should see your `face-audit-api` repo in the list. Click **Connect**.
    *(If you don't see it, click "Configure GitHub App" to give permission).*

5.  **Fill in the Settings form** exactly like this:

    | Setting | What to type |
    | :--- | :--- |
    | **Name** | `face-audit-app` (This will be in your URL) |
    | **Region** | Choose currently closest to you (e.g., Singapore, Oregon) |
    | **Branch** | `main` |
    | **Runtime** | `Python 3` |
    | **Build Command** | `pip install -r requirements.txt` |
    | **Start Command** | `gunicorn app:app --workers 1 --threads 8` |

    > **⚠️ IMORTANT:** The **Start Command** above prevents your app from crashing. Make sure you copy it exactly!

6.  **Environment Variables (Optional/Advanced)**:
    *   Scroll down to "Environment Variables".
    *   Add Key: `PYTHON_VERSION` | Value: `3.12.0`
    *   *(This ensures we use the best Python version for MediaPipe)*

7.  **Plan Type**: Select **Free**.
8.  Click **"Create Web Service"**.

---

## 🎉 Phase 4: It's Alive!

Render will now show you a black terminal screen with logs.
1.  Wait about **3-5 minutes**.
2.  It will install all libraries (numpy, opencv, flask...).
3.  Finally, you will see: `Your service is live 🎉`.
4.  Click the URL at the top left (it looks like `https://face-audit-app.onrender.com`).

**Congratulations!** Your app is now online. send the link to anyone!

---

## ❓ Common Questions (The "What Ifs")

**Q: My upload disappeared the next day!**
**A:** Yes, that is normal. Render's free servers restart every day to stay fresh. files uploaded to local disk are deleted. This is good for security!

**Q: The site takes 30 seconds to load the first time.**
**A:** Ensure on the Free Tier, if nobody visits for 15 mins, the server "goes to sleep". The first person to visit wakes it up (takes ~30s). Paid plans stay awake 24/7.

**Q: I updated my code. How do I update the live site?**
**A:** Just run these 3 commands in your terminal:
```bash
git add .
git commit -m "Fixed a bug"
git push
```
Render sees the new code on GitHub and **automatically updates** your website!

---

## 🆘 Troubleshooting

**Error: "Build Failed"**
- Check the logs. Did you forget to update `requirements.txt`?
- Did you set `PYTHON_VERSION` to `3.12.0`?

**Error: "Server Error" on Upload**
- Is your file > 100MB? The app blocks big files.
- Refresh the page and try again.

---

**You are now a SaaS Developer! 🎈**
