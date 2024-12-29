# AutoByteus Development Environment

This project provides a Docker-based development environment for AutoByteus, featuring a headless browser environment with VNC access, allowing you to interact with a full Chrome browser instance remotely.

## Prerequisites

- Docker and Docker Compose installed on your system
- A VNC viewer application installed on your client machine

## Architecture

The environment consists of two main components:
1. Base image (`Dockerfile.base`): Contains all system dependencies and Python packages
2. Development image (`Dockerfile.dev`): Configures the development environment with mounted volumes

## Getting Started

1. Build the base image first:
```bash
docker build -t autobyteus-base:latest -f Dockerfile.base .
```

2. Start the development environment:
```bash
docker-compose up -d
```

## Project Structure

The environment mounts the following directories:
- `/home/ryan-ai/SSD/autobyteus_workspace/brui_core`
- `/home/ryan-ai/SSD/autobyteus_workspace/autobyteus`
- `/home/ryan-ai/SSD/autobyteus_workspace/autobyteus-server`

## VNC Access

The container exposes port 5900 for VNC access.
Default VNC password: `mysecretpassword`

### Recommended VNC Client: TigerVNC

TigerVNC offers high performance and robust features.

#### Installation

**Windows:**
1. Download TigerVNC from the [official website](https://tigervnc.org/downloads/)
2. Run the installer
3. Launch TigerVNC Viewer
4. Connect to `localhost:5900`

**macOS:**
```bash
brew install tiger-vnc
vncviewer localhost:5900
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install tigervnc-viewer

# Fedora
sudo dnf install tigervnc

# Arch Linux
sudo pacman -S tigervnc

# Connect
vncviewer localhost:5900
```

### Alternative VNC Clients

#### Windows
- RealVNC Viewer
- TightVNC

#### macOS
- Built-in VNC viewer: `vnc://localhost:5900`
- RealVNC Viewer

#### Linux
- Remmina: `remmina -c vnc://localhost:5900`
- Vinagre: `vinagre localhost:5900`

## Environment Details

- Ubuntu 22.04 base system
- XFCE4 desktop environment
- Google Chrome browser
- Python 3.8+
- Screen resolution: 1280x1024

## Exposed Ports
- 5900: VNC access
- 9223: Chrome remote debugging
- 8000: FastAPI server

## Troubleshooting

### Connection Issues

1. Check container status:
```bash
docker ps
docker-compose logs
```

2. Verify port availability:
```bash
netstat -an | grep 5900
```

### Black Screen
```bash
docker-compose restart
docker-compose logs
```

### Development Issues

1. Check mounted volumes:
```bash
docker-compose exec app ls -la /home/vncuser/workspace
```

2. Verify Python environment:
```bash
docker-compose exec app pip list
```

3. Check FastAPI logs:
```bash
docker-compose exec app cat /var/log/supervisor/fastapi.log
```

## Security Notes

- Change the default VNC password for production use
- VNC traffic is unencrypted by default
- Use SSH tunneling for secure remote access:
```bash
ssh -L 5900:localhost:5900 user@remote-host
```

## Performance Tips

1. TigerVNC options:
   - Quality adjustment: `-quality 0-9`
   - Enable compression: `-compress`
   - Encoding options: `-encoding tight|zrle|hextile`

2. Resource optimization:
   - Mount pip cache for faster package installation
   - Use BuildKit for efficient Docker builds

## License

This project is open-source and available under the MIT license.

## Authors

Ryan Zheng (ryan.zheng.work@gmail.com)
