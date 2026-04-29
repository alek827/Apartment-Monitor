# Chestnut Square Telegram Monitor

This bot monitors https://www.chestnut-square.com/floor-plan-results for new apartment listings and sends a notification to Telegram when a new listing appears or is removed.

## Setup

1. Open a terminal in the project folder:

```bash
cd ~/Telegram\ bot
```

2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Set the Telegram bot credentials:

```bash
export TELEGRAM_BOT_TOKEN="<your bot token>"
```

The chat ID is pre-configured to your Telegram account (ID: 6611505561).

## Usage

### Test current page and payload

```bash
TELEGRAM_BOT_TOKEN="<your bot token>" python3 monitor.py --test
```

This fetches the current page, extracts the first detected listing, and sends it as a test notification.

### Run the monitor once

```bash
TELEGRAM_BOT_TOKEN="<your bot token>" python3 monitor.py
```

This will check the page, compare listings against the saved `seen.json`, and send Telegram notifications for new or removed listings.

### Dry run

```bash
TELEGRAM_BOT_TOKEN="<your bot token>" python3 monitor.py --dry-run
```

This prints the notifications that would be sent without actually sending them.

## Publish to GitHub

The `deploy.sh` script prepares this repository and pushes it to GitHub.
It requires a `GITHUB_TOKEN` environment variable and does not store the token in the repo.

```bash
export GITHUB_TOKEN="<your token>"
./deploy.sh
```

## Railway Deployment

This repo includes a GitHub Actions workflow at `.github/workflows/railway-deploy.yml`.
Once you add `RAILWAY_TOKEN`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID` as GitHub secrets, every push to `main` will deploy the app to Railway.

## 24/7 Monitoring (macOS)

To run the monitor continuously, a launchd service has been configured to check the website every 10 minutes.

### Start monitoring

```bash
launchctl load ~/Library/LaunchAgents/com.alek.apartmentmonitor.plist
```

### Stop monitoring

```bash
launchctl unload ~/Library/LaunchAgents/com.alek.apartmentmonitor.plist
```

### View logs

```bash
tail -f ~/Telegram\ bot/monitor.log
tail -f ~/Telegram\ bot/monitor.err
```

### Check status

```bash
launchctl list | grep apartmentmonitor
```

## Notes

- The target page is protected by Cloudflare, so this script uses `cloudscraper` to fetch the page.
- The script stores listing fingerprints in `seen.json` to detect newly added or removed apartments.
- The script tries to find listing blocks by looking for floor-plan related text and images.
- For 24/7 monitoring, the launchd daemon runs every 10 minutes (configurable in the .plist file).
