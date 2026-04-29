#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Initializing git repository..."
rm -rf .git 2>/dev/null || true
git init

echo "Configuring git..."
git config user.email "alek@local"
git config user.name "Alek"

echo "Adding files..."
git add .

echo "Creating commit..."
git commit -m "Initial apartment monitor setup"

echo "Adding remote origin..."
if [ -z "$GITHUB_TOKEN" ]; then
  echo "Error: GITHUB_TOKEN environment variable is not set."
  echo "Set it before running this script, for example:"
  echo "  export GITHUB_TOKEN=\"<your token>\""
  exit 1
fi

git remote add origin https://x-access-token:${GITHUB_TOKEN}@github.com/alek827/Apartment-Monitor.git

echo "Renaming branch to main..."
git branch -M main

echo "Pushing to GitHub..."
git push -u origin main

echo "✓ Successfully pushed to GitHub!"
echo "Repository: https://github.com/alek827/apartment-monitor"
