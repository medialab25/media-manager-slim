#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load configuration
if [ -f "config.json" ]; then
    CONFIG=$(cat config.json)
else
    echo -e "${RED}Error: config.json not found${NC}"
    exit 1
fi

# Function to kill all running instances
killall() {
    echo -e "${YELLOW}Stopping all running instances...${NC}"
    
    # Kill Flask development server
    pkill -f "flask run"
    
    # Kill Gunicorn processes
    pkill -f "gunicorn"
    
    # Kill any remaining Python processes from this app
    pkill -f "python.*app"
    
    echo -e "${GREEN}All instances stopped${NC}"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
}

# Function to setup environment and install dependencies
setup() {
    check_venv
    echo -e "${YELLOW}Installing dependencies...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt
}

# Function to uninstall
uninstall() {
    echo -e "${YELLOW}Uninstalling...${NC}"
    
    # Kill all running instances first
    killall
    
    # Remove virtual environment
    if [ -d "venv" ]; then
        echo -e "${YELLOW}Removing virtual environment...${NC}"
        rm -rf venv
    fi
    
    # Remove systemd service if it exists
    if [ -f "/etc/systemd/system/media-manager.service" ]; then
        echo -e "${YELLOW}Removing systemd service...${NC}"
        sudo systemctl stop media-manager
        sudo systemctl disable media-manager
        sudo rm /etc/systemd/system/media-manager.service
        sudo systemctl daemon-reload
    fi
    
    # Remove any generated files
    if [ -f "__pycache__" ]; then
        echo -e "${YELLOW}Removing Python cache files...${NC}"
        find . -type d -name "__pycache__" -exec rm -r {} +
    fi
    
    echo -e "${GREEN}Uninstall complete${NC}"
}

# Function to run development server
run_dev() {
    # Kill any existing instances first
    killall
    
    check_venv
    source venv/bin/activate
    echo -e "${GREEN}Starting development server...${NC}"
    export FLASK_ENV=development
    export FLASK_APP=app
    flask run --host=0.0.0.0 --port=5000
}

# Function to run production server
run_prod() {
    # Kill any existing instances first
    killall
    
    check_venv
    source venv/bin/activate
    echo -e "${GREEN}Starting production server...${NC}"
    export FLASK_ENV=production
    export FLASK_APP=app
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
}

# Function to install systemd service
install() {
    echo -e "${YELLOW}Installing systemd service...${NC}"
    cat > /etc/systemd/system/media-manager.service << EOL
[Unit]
Description=Media Manager Service
After=network.target

[Service]
User=media
Group=media
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOL
    echo -e "${GREEN}Service file installed at /etc/systemd/system/media-manager.service${NC}"
}

# Main script
case "$1" in
    "setup")
        setup
        ;;
    "uninstall")
        uninstall
        ;;
    "dev")
        run_dev
        ;;
    "prod")
        run_prod
        ;;
    "install")
        install
        ;;
    "killall")
        killall
        ;;
    *)
        echo "Usage: $0 {setup|uninstall|dev|prod|install|killall}"
        exit 1
        ;;
esac 