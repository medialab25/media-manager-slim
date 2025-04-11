# Media Merge

## Details
- Merge multiple folders representing different qualities to single folder
- All merging done via linux hard links
- Source folders must follow the naming pattern: `{type}-{quality}` (e.g., `tv-hd`, `tv-uhd`, `tv-4k`)
- Multiple types can exist, each with their own set of quality levels
- Types are completely independent - no shared configuration
- Quality levels are defined globally and used by all types
- Missing quality levels for a type are allowed and ignored
- All directories (source and merged) must be on the same physical drive to allow hard links
- No restrictions on file naming within the folders
- No restrictions on file types or extensions
- No size limitations on files or directories
- Supports any number of quality levels through additional source folders
- Files are matched based on identical folder names across quality levels
- Folder structure is always flat, with each folder representing a movie or TV show
- File names can be different between quality levels
- Folders can contain multiple files
- Folder names are preserved exactly as in the source
- If a source file is updated, the hard link will point to the new version

## Configuration
- Types and their paths are defined in config.json
- Quality levels are defined globally and used by all types
- No validation steps needed for directory structure
- Assumes all directories are on the same physical drive
- Merged directories are created automatically if they don't exist
- Created directories are owned by the user:group specified in config.json
- Created directories have permissions 755 (drwxr-xr-x)
- All paths in config.json must be absolute

### config.json Template
```json
{
    "user": "username",
    "group": "groupname",
    "quality_order": ["4k", "uhd", "hd", "sd"],  // Highest to lowest quality
    "types": {
        "tv": {
            "source_paths": [
                "/absolute/path/to/tv-4k",
                "/absolute/path/to/tv-uhd",
                "/absolute/path/to/tv-hd"
            ],
            "merged_path": "/absolute/path/to/tv-merged"
        },
        "movies": {
            "source_paths": [
                "/absolute/path/to/movies-4k",
                "/absolute/path/to/movies-uhd",
                "/absolute/path/to/movies-hd"
            ],
            "merged_path": "/absolute/path/to/movies-merged"
        }
    }
}
```

## Process Flow
1. Read and parse config.json
2. For each type defined in config:
   a. Create merged directory if it doesn't exist
   b. Set merged directory ownership to user:group from config
   c. Set merged directory permissions to 755
3. For each type:
   a. For each source path in order (highest to lowest quality):
      i. Extract quality from path name
      ii. If quality matches a defined quality level:
          - Scan source directory for folders
          - For each folder found:
            * If folder doesn't exist in merged directory:
              - Create folder in merged directory with same name as source
              - Set ownership and permissions
              - For each file in the folder:
                - Create hard link
                - Preserve original file's permissions and ownership
            * If folder exists in merged directory:
              - Skip (already have higher quality version)
4. Complete when all types and qualities processed

## File Operations
- Hard links preserve original file's permissions and ownership
- Existing files in merged directory are removed before creating new hard links
- Only new hard links are created when needed
- No files are copied or moved, only hard linked
- Files are matched based on identical folder names across quality levels
- File names can be different between quality levels
- All files in a folder are processed
- If a source file is updated, the hard link automatically points to the new version
- Example:
  ```
  tv-hd/movie_1/
    - film-hd.mkv
    - extras-hd.mkv
    - subtitles.srt
  matches
  tv-uhd/movie_1/
    - film-uhd.mkv
    - extras-uhd.mkv
    - subtitles.srt
  ```

## Error Handling
- All errors are caught and handled generically
- Process assumes user:group exists on the system
- No special error handling for permission or ownership issues
- Missing source paths are skipped
- Invalid quality levels in path names are skipped
- Directory creation errors are reported
- File linking errors are reported

## Requirements
- Only delete a hard link if it is going to be updated with a different source file
- If the new link would point to the same source file, keep the existing link
- Link verification method: TBD
- No special error handling needed for failed operations

## Examples

### Basic operation with multiple types

Example Workflow:
For each type (e.g., tv, movies):
- Uses globally defined quality levels
- Missing quality levels are ignored
- If a file exists in the highest available quality source (e.g., tv-uhd), it will be used
- If it only exists in lower quality sources (e.g., tv-hd), that version will be used
- The result is a single directory per type containing the best available quality for each file

Input:
- tv-hd/movie_1/film-hd.mkv
- tv-hd/movie_2/film-hd.mkv
- tv-uhd/movie_1/film-uhd.mkv
- movies-hd/film_1/movie-hd.mkv
- movies-uhd/film_1/movie-uhd.mkv

- Global quality order: 4k > uhd > hd > sd
- Note: tv type missing 4k quality, movies type missing sd quality

Action:
- Take all files in highest available quality for each type
- Take all files from lower qualities if not already merged
- Create merged directories if they don't exist

Output:
- tv-merged/movie_1/film-uhd.mkv
- tv-merged/movie_2/film-hd.mkv
- movies-merged/film_1/movie-uhd.mkv

### Add uhd film and re-merge (hd also exists)

Input:
- tv-hd/movie_1/film-hd.mkv
- tv-merged/movie_1/film-hd.mkv

Action:
- Add new file: tv-uhd/movie_1/film-uhd.mkv
- Re-run merge with sources: tv-uhd, tv-hd

Output:
- tv-merged/movie_1/film-uhd.mkv (replaces hd version)

### Add hd film and re-merge (hd added but no uhd)

Input:
- tv-merged/ (empty)
- tv-uhd/ (empty)

Action:
- Add new file: tv-hd/movie_1/film-hd.mkv
- Run merge with sources: tv-uhd, tv-hd

Output:
- tv-merged/movie_1/film-hd.mkv

### Remove uhd film and re-merge (hd also exists)

Input:
- tv-uhd/movie_1/film-uhd.mkv
- tv-hd/movie_1/film-hd.mkv
- tv-merged/movie_1/film-uhd.mkv

Action:
- Remove file: tv-uhd/movie_1/film-uhd.mkv
- Re-run merge with sources: tv-uhd, tv-hd

Output:
- tv-merged/movie_1/film-hd.mkv (falls back to hd version)

### Remove uhd film and re-merge (hd does not exist)

Input:
- tv-uhd/movie_1/film-uhd.mkv
- tv-merged/movie_1/film-uhd.mkv

Action:
- Remove file: tv-uhd/movie_1/film-uhd.mkv
- Re-run merge with sources: tv-uhd, tv-hd

Output:
- tv-merged/movie_1/ (empty, file removed as no alternative exists)

### Have uhd and not hd

Input:
- tv-uhd/movie_1/film-uhd.mkv
- tv-hd/ (empty)

Action:
- Run merge with sources: tv-uhd, tv-hd

Output:
- tv-merged/movie_1/film-uhd.mkv

## API Endpoints

### GET /media/merge/status
Returns the current configuration status including:
- User and group settings
- Quality order
- Source paths and merged paths for each media type

Example Response:
```json
{
    "status": "ok",
    "config": {
        "user": "media",
        "group": "media",
        "quality_order": ["4k", "uhd", "hd", "sd"],
        "types": {
            "tv": {
                "source_paths": [
                    "/media/tv-4k",
                    "/media/tv-uhd",
                    "/media/tv-hd"
                ],
                "merged_path": "/media/tv-merged"
            },
            "movies": {
                "source_paths": [
                    "/media/movies-4k",
                    "/media/movies-uhd",
                    "/media/movies-hd"
                ],
                "merged_path": "/media/movies-merged"
            }
        }
    }
}
```

### POST /media/merge
Starts the media merge process. Returns success when complete.

Example Response:
```json
{
    "status": "ok",
    "message": "Merge process completed successfully"
}
```

Error Response:
```json
{
    "status": "error",
    "message": "Error message describing the issue"
}
```

## Frequently Asked Questions

### File Naming
- Files can have any name within the source directories
- The system matches files based on their relative paths within the quality folders

### Directory Structure
- Source directories must follow the pattern: `{type}-{quality}`
- Each source directory can contain multiple folders
- Each folder represents a movie or TV show
- The folder structure is flat (no subdirectories)
- All files within a folder are processed
- File names can differ between quality levels