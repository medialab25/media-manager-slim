# Overview

## Summary
- named: media-manager-slim
- Linux service that accepts http requests to perform function
- Codebase: Python
- Dependencies: Flask
- Uses systemd as framework

## Requirements
- Python version requirements: >= 3.8
- All function managed via a manage.sh script
  - start/stop/enable/disable/dev/setup
- All setup via a config.json
  - Additional functions can be added to it
- requirements.txt used for dependencies and dev has own file
- Use Flaks and blueprints:
  - system
  - media

### Endpoints:
- health
  - Checks the service is running. Return 200 is healthy

- media
  - Handles the media control functions

### Media Control Functions
- Specific functions to be implemented in the `/media` endpoint:
  - refresh
  - merge
  - rebuild-cache
- Parameters to be specified

### Config.Json
- Can be expanded
- Example for basic project structure:
- Have a global Config loader

```
{
    port: 5000
    url: 0.0.0.0
    // Any options needed to support dev. env
}
```

### Structure

Project:
- src/
  - <component>/
  - main.py
- docs/
- README.md
- manage.sh
- config.json

## Dev. Environment
- Virtual environment tool: venv
- Hot reloading: flasks builtin
- Work without need for systemd
- All options accessible via the manage.sh

## Not required
- Testing
- Security

