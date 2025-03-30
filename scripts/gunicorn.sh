#!/usr/bin/bash

if [ -f "/home/ubuntu/Ecommerce_API/gunicorn/gunicorn.socket" ]; then
    sudo cp /home/ubuntu/Ecommerce_API/gunicorn/gunicorn.socket /etc/systemd/system/gunicorn.socket
else
    echo "gunicorn.socket not found!"
fi

if [ -f "/home/ubuntu/Ecommerce_API/gunicorn/gunicorn.service" ]; then
    sudo cp /home/ubuntu/Ecommerce_API/gunicorn/gunicorn.service /etc/systemd/system/gunicorn.service
else
    echo "gunicorn.service not found!"
fi

# Reload systemd to apply changes
sudo systemctl daemon-reload

# Start and enable Gunicorn service
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service
