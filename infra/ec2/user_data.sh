#!/bin/bash
set -e

# Update system
apt-get update -y
apt-get upgrade -y

# Install dependencies
apt-get install -y python3 python3-pip python3-venv git nginx

# Clone your repo
cd /home/ubuntu
git clone https://github.com/ailojay/ai-chatbot.git
cd ai-chatbot

# Create virtual environment and install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with the API key
cat > /home/ubuntu/ai-chatbot/.env << EOF
GEMINI_API_KEY=${gemini_api_key}
EOF

# Set correct permissions
chown -R ubuntu:ubuntu /home/ubuntu/ai-chatbot

# Create systemd service so app restarts automatically
cat > /etc/systemd/system/ai-chatbot.service << EOF
[Unit]
Description=AI Chatbot Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-chatbot
Environment="PATH=/home/ubuntu/ai-chatbot/venv/bin"
ExecStart=/home/ubuntu/ai-chatbot/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable ai-chatbot
systemctl start ai-chatbot

# Configure nginx as reverse proxy
cat > /etc/nginx/sites-available/ai-chatbot << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

# Enable nginx site
ln -s /etc/nginx/sites-available/ai-chatbot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
systemctl enable nginx