# Deploy to Railway (Cloud Server)

This guide shows how to deploy the apartment monitor to Railway.app for 24/7 monitoring without keeping your Mac on.

## Prerequisites

1. A GitHub account (free at github.com)
2. A Railway account (free at railway.app)

## Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `apartment-monitor`
3. Choose "Public" or "Private" (your choice)
4. Click "Create repository"

## Step 2: Push Code to GitHub

Run these commands in your terminal:

```bash
cd ~/Telegram\ bot
git init
git add .
git commit -m "Initial apartment monitor setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/apartment-monitor.git
git push -u origin main
```

(Replace `YOUR_USERNAME` with your actual GitHub username)

## Step 3: Deploy to Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select the `apartment-monitor` repository
4. Railway will auto-detect the Python project
5. Wait for the build to complete

## Step 4: Set Environment Variables

In Railway dashboard:

1. Click on your project
2. Go to "Variables" tab
3. Add these environment variables:
   - **TELEGRAM_BOT_TOKEN**: `8709174064:AAEmYg0RHtSZ2yPij_iFvk2cCADCN38u1pA`
   - **TELEGRAM_CHAT_ID**: `6611505561` (optional, has default)

## Step 5: Deploy

1. Railway will automatically deploy from your GitHub repo
2. Go to "Deployments" tab
3. You should see logs showing "Starting apartment monitor..."

## That's it!

Your monitor now runs 24/7 on Railway's servers. It will:
- Check the Chestnut Square website every 3 minutes
- Send Telegram notifications when new apartments appear
- Continue running even if your Mac is off

### Monitoring

To view live logs from Railway:
1. Go to your Railway project
2. Click "View Logs" 
3. You'll see real-time output from the monitor

### Optional: Update Deployment

To pull code changes from your Mac to the cloud:

```bash
cd ~/Telegram\ bot
git add .
git commit -m "Update: description of changes"
git push
```

Railway will automatically redeploy with your latest code.

## Troubleshooting

If the monitor isn't running:
1. Check Railway logs for errors
2. Verify environment variables are set correctly
3. Make sure the GitHub repo was pushed with all files (Procfile, requirements.txt, monitor.py, server.py)

## Free Tier Limits

Railway's free tier includes:
- 500 hours per month ($5 credit = ~600 hours with single dyno)
- Enough for 24/7 monitoring on 1 worker
