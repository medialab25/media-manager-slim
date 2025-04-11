# Overview

## Summary
- named: media-manager-slim
- Linux service that accepts http requests to perform function
- Codebase: Python
- Dependencies: Flask, requests
- Uses systemd as framework

## Requirements
- Python version requirements: >= 3.8
- All function managed via a manage.sh script
  - start/stop/enable/disable/dev/setup
- All setup via a config.json
  - Additional functions can be added to it
- requirements.txt used for dependencies and dev has own file
- Use Flask and blueprints:
  - system
  - media

### Endpoints:
- health
  - Checks the service is running. Return 200 is healthy

- media
  - Handles the media control functions
  - Base URL: /media
  - Endpoints:
    - POST /refresh
      - Returns 200 OK with status message
      - Makes request to JellyFin API to refresh libraries
      - Error responses:
        - 500: JellyFin server unreachable
        - 401: Invalid JellyFin token
        - 400: Other JellyFin API errors

### Media Control Functions
- Specific functions to be implemented in the `/media` endpoint:
  - refresh (Implemented as POST endpoint)
    - Returns: {"status": "ok", "message": "..."} on success
    - Returns: {"status": "error", "message": "..."} on failure
  - merge (To be implemented)
  - rebuild-cache (To be implemented)
- Parameters to be specified

### Config.Json
- Current structure:
```json
{
    "DEBUG": false,
    "HOST": "0.0.0.0",
    "PORT": 5000,
    "JELLYFIN": {
        "URL": "http://your-jellyfin-server",
        "TOKEN": "your-api-token"
    }
}
```
- Required fields:
  - DEBUG: boolean
  - HOST: string
  - PORT: number
  - JELLYFIN.URL: string
  - JELLYFIN.TOKEN: string
- Have a global Config loader in app/__init__.py

### Structure

Project:
- app/
  - __init__.py (App factory and config loader)
  - routes/
    - main.py (System endpoints)
    - media.py (Media control endpoints)
- docs/
- README.md
- manage.sh
- config.json
- requirements.txt

## Dev. Environment
- Virtual environment tool: venv
- Hot reloading: Flask's built-in development server
- Work without need for systemd
- All options accessible via the manage.sh
- Development server runs on 0.0.0.0:5000 by default

## Not required
- Testing
- Security

