#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check sudo privileges
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}Error: This command requires sudo privileges${NC}"
        echo -e "${YELLOW}Please run with sudo: sudo ./manage.sh $1${NC}"
        exit 1
    fi
}

# Load configuration
if [ -f "config.json" ]; then
    CONFIG=$(cat config.json)
else
    echo -e "${RED}Error: config.json not found${NC}"
    exit 1
fi

# Function to check status
status() {
    echo -e "${YELLOW}Checking application status...${NC}"
    
    # Check if Flask or Gunicorn processes are running
    if pgrep -f "flask run" > /dev/null || pgrep -f "gunicorn" > /dev/null || pgrep -f "python.*app" > /dev/null; then
        echo -e "${GREEN}Application is running${NC}"
        echo "Running processes:"
        pgrep -f "flask run" | xargs -r ps -fp
        pgrep -f "gunicorn" | xargs -r ps -fp
        pgrep -f "python.*app" | xargs -r ps -fp
    else
        echo -e "${RED}Application is not running${NC}"
    fi
    
    # Check systemd service status
    if [ -f "/etc/systemd/system/media-manager.service" ]; then
        echo -e "\n${YELLOW}Systemd service status:${NC}"
        systemctl status media-manager --no-pager
    else
        echo -e "\n${YELLOW}Systemd service is not installed${NC}"
    fi
    
    # Check virtual environment
    if [ -d "venv" ]; then
        echo -e "\n${GREEN}Virtual environment exists${NC}"
    else
        echo -e "\n${RED}Virtual environment does not exist${NC}"
    fi
}

# Function to start the application
start() {
    if [ -f "/etc/systemd/system/media-manager.service" ]; then
        echo -e "${YELLOW}Starting via systemd...${NC}"
        check_sudo "start"
        sudo systemctl start media-manager
    else
        echo -e "${YELLOW}Starting in production mode...${NC}"
        run_prod
    fi
}

# Function to stop the application
stop() {
    if [ -f "/etc/systemd/system/media-manager.service" ]; then
        echo -e "${YELLOW}Stopping via systemd...${NC}"
        check_sudo "stop"
        sudo systemctl stop media-manager
    else
        echo -e "${YELLOW}Stopping all instances...${NC}"
        killall
    fi
}

# Function to restart the application
restart() {
    if [ -f "/etc/systemd/system/media-manager.service" ]; then
        echo -e "${YELLOW}Restarting via systemd...${NC}"
        check_sudo "restart"
        sudo systemctl restart media-manager
    else
        echo -e "${YELLOW}Restarting application...${NC}"
        stop
        sleep 2
        start
    fi
}

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
        check_sudo "uninstall"
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
    gunicorn -w 1 -b 0.0.0.0:5000 app:application
}

# Function to install systemd service
install() {
    check_sudo "install"
    echo -e "${YELLOW}Installing systemd service...${NC}"
    
    # Create log directory if it doesn't exist
    sudo mkdir -p /var/log/media-manager
    
    # Get the absolute path to the project directory
    PROJECT_DIR=$(pwd)
    
    cat > /etc/systemd/system/media-manager.service << EOL
[Unit]
Description=Media Manager Service
After=network.target
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
Type=simple
User=media
Group=media
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${PROJECT_DIR}/venv/bin"
Environment="PYTHONPATH=${PROJECT_DIR}"
Environment="FLASK_APP=app"
Environment="FLASK_ENV=production"
ExecStart=${PROJECT_DIR}/venv/bin/python3 ${PROJECT_DIR}/venv/bin/gunicorn --access-logfile /var/log/media-manager/access.log --error-logfile /var/log/media-manager/error.log -w 1 -b 0.0.0.0:5000 app:application
Restart=on-failure
RestartSec=5s
TimeoutStartSec=30
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOL
    echo -e "${GREEN}Service file installed at /etc/systemd/system/media-manager.service${NC}"
    
    # Set proper permissions for log directory
    sudo chown -R media:media /var/log/media-manager
    
    # Reload systemd to pick up the new service file
    sudo systemctl daemon-reload
    echo -e "${YELLOW}Systemd daemon reloaded${NC}"
    
    # Enable the service to start on boot
    sudo systemctl enable media-manager
    echo -e "${YELLOW}Service enabled to start on boot${NC}"
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
    "status")
        status
        ;;
    "start")
        start
        ;;
    "stop")
        stop
        ;;
    "restart")
        restart
        ;;
    *)
        echo "Usage: $0 {setup|uninstall|dev|prod|install|killall|status|start|stop|restart}"
        exit 1
        ;;
esac 