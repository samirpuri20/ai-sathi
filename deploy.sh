#!/bin/bash

echo "🚀 AI Sathi Deployment Script"
echo "=============================="

echo "Choose deployment option:"
echo "1. Heroku (Free/Paid)"
echo "2. Railway (Free)"
echo "3. Render (Free)"
echo "4. Local Network (Free)"
echo "5. Ngrok Tunnel (Free)"

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "📦 Deploying to Heroku..."
        echo "1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
        echo "2. Run: heroku login"
        echo "3. Run: heroku create ai-sathi-app"
        echo "4. Run: git init && git add . && git commit -m 'Deploy AI Sathi'"
        echo "5. Run: heroku config:set GEMINI_API_KEY=AIzaSyBOukE7ak1vmIFR7zaiOvmCBVXDc0xf7ZE"
        echo "6. Run: git push heroku main"
        ;;
    2)
        echo "🚂 Deploying to Railway..."
        echo "1. Go to: https://railway.app"
        echo "2. Connect GitHub and deploy this folder"
        echo "3. Add environment variable: GEMINI_API_KEY=AIzaSyBOukE7ak1vmIFR7zaiOvmCBVXDc0xf7ZE"
        ;;
    3)
        echo "🎨 Deploying to Render..."
        echo "1. Go to: https://render.com"
        echo "2. Create new Web Service from GitHub"
        echo "3. Build Command: pip install -r requirements.txt"
        echo "4. Start Command: python deploy_config.py"
        echo "5. Add environment variable: GEMINI_API_KEY=AIzaSyBOukE7ak1vmIFR7zaiOvmCBVXDc0xf7ZE"
        ;;
    4)
        echo "🏠 Starting Local Network Server..."
        echo "AI Sathi will be accessible on your local network"
        python3 -c "
import socket
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
print(f'🌐 Access AI Sathi at: http://{local_ip}:5000')
print('📱 Use this URL on any device on your network')
"
        python3 deploy_config.py
        ;;
    5)
        echo "🌐 Creating Ngrok Tunnel..."
        if command -v ngrok &> /dev/null; then
            echo "Starting AI Sathi and creating public tunnel..."
            python3 deploy_config.py &
            sleep 3
            ngrok http 5000
        else
            echo "❌ Ngrok not installed"
            echo "1. Install: brew install ngrok"
            echo "2. Sign up: https://ngrok.com"
            echo "3. Run: ngrok authtoken YOUR_TOKEN"
            echo "4. Run this script again"
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac