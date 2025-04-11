# Media Manager Slim

A lightweight Flask-based media management application.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- systemd (for production deployment)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd media-manager-slim
```

2. Make the manage script executable:
```bash
chmod +x manage.sh
```

3. Setup the environment and install dependencies:
```bash
./manage.sh setup
```

## Uninstallation

To completely remove the application and its dependencies:
```bash
./manage.sh uninstall
```

This will:
- Remove the virtual environment
- Remove the systemd service (if installed)
- Clean up Python cache files

## Process Management

To stop all running instances of the application:
```bash
./manage.sh killall
```

This will:
- Stop any running Flask development servers
- Stop any running Gunicorn processes
- Stop any other Python processes from this application

## Configuration

The application uses `config.json` for configuration. Update the following settings as needed:

```json
{
    "DEBUG": false,
    "HOST": "0.0.0.0",
    "PORT": 5000
}
```

## Development

To run the application in development mode (with hot-reloading):
```bash
./manage.sh dev
```

The development server will be available at `http://localhost:5000`

## Production Deployment

### Without systemd

To run the application in production mode:
```bash
./manage.sh prod
```

### With systemd

1. Install the systemd service:
```bash
sudo ./manage.sh install
```

2. Enable and start the service:
```bash
sudo systemctl enable media-manager
sudo systemctl start media-manager
```

3. Check the service status:
```bash
sudo systemctl status media-manager
```

## API Endpoints

- `GET /`: Health check endpoint
  ```json
  {
    "status": "ok",
    "message": "Media Manager API is running"
  }
  ```

- `GET /health`: Version information
  ```json
  {
    "status": "ok",
    "version": "1.0.0"
  }
  ```

- `POST /media/merge`: Start the media merge process
  ```json
  {
    "status": "ok",
    "message": "Merge process completed successfully"
  }
  ```

- `GET /media/merge/status`: Get current status of media merge configuration
  ```json
  {
    "status": "ok",
    "config": {
      "user": "media",
      "group": "media",
      "quality_order": ["4k", "uhd", "hd", "sd"],
      "types": {
        "tv": {
          "source_paths": ["/path/to/source"],
          "merged_path": "/path/to/merged"
        },
        "movies": {
          "source_paths": ["/path/to/source"],
          "merged_path": "/path/to/merged"
        }
      }
    }
  }
  ```

- `POST /media/refresh`: Refresh JellyFin libraries
  ```json
  {
    "status": "ok",
    "message": "Successfully refreshed JellyFin libraries"
  }
  ```

## Media Merge Configuration

The media merge feature allows you to combine media files from multiple source paths into a single merged location, with automatic quality selection based on a priority order.

### Configuration

Add the following to your `config.json`:

```json
{
  "MEDIA_MERGE": {
    "user": "media",
    "group": "media",
    "quality_order": ["4k", "uhd", "hd", "sd"],
    "types": {
      "tv": {
        "source_paths": ["/path/to/source"],
        "merged_path": "/path/to/merged"
      },
      "movies": {
        "source_paths": ["/path/to/source"],
        "merged_path": "/path/to/merged"
      }
    }
  }
}
```

### Features

1. **Quality-based Merging**
   - Files are merged based on quality order (e.g., 4k > uhd > hd > sd)
   - Higher quality versions take precedence over lower quality ones

2. **Automatic Cleanup**
   - Files that no longer exist in any source path are automatically removed from the merged location
   - Empty directories are cleaned up after file removal
   - Hard links are used to save disk space

3. **Permission Management**
   - All created directories and files maintain correct ownership and permissions
   - Uses the configured user and group for file operations

### Example

Given the following structure:
```
/source1/
  show1/
    episode1-4k.mkv
    episode2-4k.mkv
/source2/
  show1/
    episode1-hd.mkv
    episode2-hd.mkv
```

After merging with quality order ["4k", "hd"], the merged location will contain:
```
/merged/
  show1/
    episode1-4k.mkv  (from source1)
    episode2-4k.mkv  (from source1)
```

If a file is removed from all source paths, it will be automatically removed from the merged location during the next merge operation.

## Project Structure

```
media-manager-slim/
├── app/
│   ├── __init__.py
│   └── routes/
│       └── main.py
├── config.json
├── manage.sh
├── requirements.txt
└── README.md
```

## Troubleshooting

1. **Virtual Environment Issues**
   - If you encounter issues with the virtual environment, try removing it and reinstalling:
   ```bash
   rm -rf venv
   ./manage.sh install
   ```

2. **Port Already in Use**
   - If port 5000 is already in use, update the port in `config.json`

3. **Permission Issues**
   - Ensure the `media` user and group exist for systemd deployment
   - Check file permissions if running into access issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here] 