#!/bin/bash

# QR Attendance System - Deployment Helper Script
# This script helps prepare your project for deployment

set -e

echo "🚀 QR Attendance System - Deployment Helper"
echo "==========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository already initialized"
fi

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    echo "⚠️  Warning: .gitignore not found!"
else
    echo "✅ .gitignore found"
fi

# Check if .env is in .gitignore
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo "✅ .env is in .gitignore"
else
    echo "⚠️  Warning: .env should be in .gitignore!"
fi

# Check if backend/.env exists
if [ -f backend/.env ]; then
    echo "✅ backend/.env found"
    echo "⚠️  Remember: DO NOT commit .env file!"
else
    echo "⚠️  backend/.env not found - you'll need to set environment variables in hosting platform"
fi

echo ""
echo "📋 Pre-deployment Checklist:"
echo "  [ ] Git repository initialized"
echo "  [ ] .env file is NOT committed"
echo "  [ ] All changes are committed"
echo "  [ ] GitHub repository created"
echo "  [ ] Service Account JSON ready"
echo ""

# Ask if user wants to commit
read -p "Do you want to commit all changes? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📝 Staging all files..."
    git add .
    
    read -p "Enter commit message: " commit_msg
    git commit -m "$commit_msg"
    echo "✅ Changes committed"
fi

echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Create a GitHub repository:"
echo "   https://github.com/new"
echo ""
echo "2. Push your code:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Choose a hosting platform:"
echo "   • Render.com (recommended): https://render.com"
echo "   • Railway.app: https://railway.app"
echo "   • Vercel (frontend): https://vercel.com"
echo ""
echo "4. Follow the deployment guide:"
echo "   See FREE_DEPLOYMENT_GUIDE.md for detailed instructions"
echo ""
echo "✨ Good luck with your deployment!"
