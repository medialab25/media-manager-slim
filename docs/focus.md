# Focus

- File to list and modify to guide cursor focus.

## Tasks:

✅ Create template, skeleton python project with Flask
- Basic Flask application structure created
- App factory pattern implemented
- Blueprint-based routing
- Basic health check endpoints

✅ Setup dev. environment
- Virtual environment setup
- Dependencies management (requirements.txt)
- Hot-reloading support
- Basic configuration system

✅ Add manage script
- Installation function
- Development server with hot-reloading
- Production server with gunicorn
- Systemd service creation
- Environment management

✅ Create config.json
- Basic configuration structure
- Host and port settings
- Debug mode toggle
- JellyFin configuration (URL and TOKEN)

✅ Add systemd service file
- Service file template
- User/group configuration
- Automatic restart
- Working directory setup

✅ Ensure manage.sh has all required functions
- install: Environment setup
- dev: Development server
- prod: Production server
- create-service: Systemd setup

✅ Ensure we have a fully running system that:
- Hot-reloads in development ✓
- Can be used without systemd ✓
- Provides a good base for adding functionality ✓

## Documentation:
✅ README.md created with:
- Installation instructions
- Configuration guide
- Development setup
- Production deployment
- API documentation
- Troubleshooting guide

## Task 2: Add media/refresh endpoint
✅ Add skeleton endpoint using the blueprint pattern with a TODO method
- Created media.py blueprint in app/routes/
- Implemented POST /media/refresh endpoint
- Added blueprint registration in app/__init__.py
- Endpoint returns 200 OK with dummy response
- Tested and verified working with curl
- Updated project documentation

## Task 3: Send request to JellyFin API
- Send request to JellyFin to refresh all libraries from the /media/refresh endpoint
- Get JellyFin url and TOKEN from config.json
- Return appropriate status codes:
  - 200: Success
  - 500: JellyFin server unreachable
  - 401: Invalid JellyFin token
  - 400: Other JellyFin API errors
- Use: https://api.jellyfin.org/#tag/Library/operation/RefreshLibrary
- Add requests library to requirements.txt

## Remaining Considerations:
- Add logging configuration
- Consider adding basic error handling middleware
- Add request/response logging
- Consider adding basic metrics endpoint
- Add backup strategy documentation
- Add monitoring setup guide
