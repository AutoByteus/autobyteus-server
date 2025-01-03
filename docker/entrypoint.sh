#!/bin/bash
set -ex

# Install local packages
echo "Installing local packages..."
cd /home/vncuser/workspace/brui_core
pip install .

cd /home/vncuser/workspace/autobyteus
pip install .

# Debug info function
debug_info() {
    echo "=== Debugging Info ==="
    echo "D-Bus Directory Contents:"
    ls -la /var/run/dbus/
    echo "Process List:"
    ps aux
    echo "System Bus Socket:"
    ls -la /var/run/dbus/system_bus_socket 2>/dev/null || echo "Socket not found"
    echo "===================="
}

# Create D-Bus directory if it doesn't exist
mkdir -p /var/run/dbus
chown messagebus:messagebus /var/run/dbus
chmod 755 /var/run/dbus

# Cleanup any existing socket
rm -f /var/run/dbus/system_bus_socket
rm -f /var/run/dbus/pid

debug_info

# Wait for socket creation after supervisord starts D-Bus
for i in {1..10}; do
    if [ -e /var/run/dbus/system_bus_socket ]; then
        echo "D-Bus socket found"
        chmod 666 /var/run/dbus/system_bus_socket
        break
    fi
    echo "Waiting for D-Bus socket... attempt $i"
    sleep 1
done

debug_info

# Detect system architecture and prepare the browser command
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"
if [ "$ARCH" = "aarch64" ]; then
    echo "Using Chromium for ARM64"
    BROWSER_COMMAND="/usr/bin/chromium-browser --no-first-run --disable-gpu --disable-software-rasterizer --disable-dev-shm-usage --no-sandbox --remote-debugging-port=9222"
elif [ "$ARCH" = "x86_64" ]; then
    echo "Using Google Chrome for AMD64"
    BROWSER_COMMAND="/usr/bin/google-chrome-stable --no-first-run --disable-gpu --disable-software-rasterizer --disable-dev-shm-usage --no-sandbox --remote-debugging-port=9222"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# Update supervisord configuration dynamically
sed -i "s|BROWSER_COMMAND_PLACEHOLDER|$BROWSER_COMMAND|" /etc/supervisor/conf.d/supervisord.conf

# Start supervisord
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
