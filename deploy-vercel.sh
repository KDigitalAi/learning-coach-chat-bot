#!/bin/bash
# Vercel Deployment Script
# This script helps deploy to Vercel with different configurations

echo "🚀 Vercel Deployment Helper"
echo "============================"
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "✅ Vercel CLI found"
echo ""

# Check current configuration
echo "📋 Current Configuration:"
echo "  - vercel.json: $(test -f vercel.json && echo '✅' || echo '❌')"
echo "  - api/index.py: $(test -f api/index.py && echo '✅' || echo '❌')"
echo "  - api/requirements.txt: $(test -f api/requirements.txt && echo '✅' || echo '❌')"
echo ""

# Ask which configuration to use
echo "Select deployment method:"
echo "1) Current vercel.json (functions format)"
echo "2) Alternative 1 (builds + routes)"
echo "3) Alternative 2 (minimal)"
echo "4) Test locally first (vercel dev)"
echo "5) Deploy to production"
read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo "Using current vercel.json..."
        ;;
    2)
        echo "Switching to builds + routes format..."
        cp vercel-alternative-1.json vercel.json
        ;;
    3)
        echo "Switching to minimal configuration..."
        cp vercel-alternative-2.json vercel.json
        ;;
    4)
        echo "Starting local development server..."
        vercel dev
        exit 0
        ;;
    5)
        echo "Deploying to production..."
        vercel --prod
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Deploy
echo ""
echo "🚀 Deploying..."
vercel

echo ""
echo "✅ Deployment initiated!"
echo "Check Vercel dashboard for status."

