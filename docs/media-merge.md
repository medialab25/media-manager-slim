# Media Merge

## Overview
A system to merge media files from multiple quality-based source folders into a single destination folder using hard links. Files from higher quality sources take precedence over lower quality versions.

## Key Features
- Creates hard links (no file duplication)
- Supports multiple media types (e.g., TV shows, movies)
- Quality-based file selection (e.g., 4K > UHD > HD > SD)
- Preserves original file permissions and ownership
- Flat directory structure (no nested folders)

## Configuration
Configuration is done via `config.json`:

```json
{
    "user": "username",
    "group": "groupname",
    "quality_order": ["4k", "uhd", "hd", "sd"],
    "types": {
        "tv": {
            "source_paths": [
                "/path/to/tv-4k",
                "/path/to/tv-uhd",
                "/path/to/tv-hd"
            ],
            "merged_path": "/path/to/tv-merged"
        },
        "movies": {
            "source_paths": [
                "/path/to/movies-4k",
                "/path/to/movies-uhd",
                "/path/to/movies-hd"
            ],
            "merged_path": "/path/to/movies-merged"
        }
    }
}
```

## Requirements
- All paths must be absolute
- All directories must be on same physical drive (for hard links)
- Source folders must follow naming pattern: `{type}-{quality}`
- User and group must exist on system

## API Endpoints

### GET /media/merge/status
Returns current configuration status.

### POST /media/merge
Triggers the merge process.

## Behavior Examples

### Quality Selection
- If a file exists in multiple qualities, highest available quality is used
- When removing a higher quality file, system falls back to next available quality
- If no quality versions exist, file is removed from merged directory

### File Structure
Source:
```
tv-hd/
  show1/
    episode-hd.mkv
tv-uhd/
  show1/
    episode-uhd.mkv
```

Result:
```
tv-merged/
  show1/
    episode-uhd.mkv  # UHD version used (higher quality)
```

## Error Handling
- Invalid configurations return 400 error
- Missing permissions return appropriate error codes
- Failed operations are logged
- Process stops on critical errors

For detailed technical implementation, see the source code in `app/routes/media.py`.