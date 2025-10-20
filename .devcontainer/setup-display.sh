#!/bin/bash
set -e

echo "🔧 Installing display environment for Pygame..."

# Install Xvfb, fluxbox (window manager), and noVNC
sudo apt-get update
sudo apt-get install -y xvfb fluxbox novnc websockify x11vnc

# Set up display startup script
cat << 'EOF' > /usr/local/bin/start-display.sh
#!/bin/bash
export DISPLAY=:1
Xvfb :1 -screen 0 1024x768x16 &
sleep 2
fluxbox &
x11vnc -display :1 -nopw -forever -shared -rfbport 5900 &
websockify --web=/usr/share/novnc/ 6080 localhost:5900
EOF

chmod +x /usr/local/bin/start-display.sh

# Run the display environment in the background
nohup /usr/local/bin/start-display.sh > /tmp/display.log 2>&1 &
echo "✅ Virtual display started on port 6080"
