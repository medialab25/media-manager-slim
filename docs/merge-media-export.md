# Media Merge - Go Implementation Specification

## Project Structure
```
media-manager/
├── cmd/
│   └── media-manager/
│       └── main.go       # Application entry point
├── internal/
│   ├── config/          # Configuration handling
│   ├── api/             # HTTP API handlers
│   ├── merge/           # Media merge core logic
│   └── utils/           # Shared utilities
├── pkg/                 # Public packages if needed
├── config.json         # Configuration file
├── go.mod             # Go module file
└── README.md          # Project documentation
```

## Core Types

```go
// Config represents the application configuration
type Config struct {
    User         string            `json:"user"`
    Group        string            `json:"group"`
    QualityOrder []string          `json:"quality_order"`
    Types        map[string]Type   `json:"types"`
}

// Type represents a media type configuration
type Type struct {
    SourcePaths []string `json:"source_paths"`
    MergedPath  string   `json:"merged_path"`
}

// MediaFile represents a media file in the system
type MediaFile struct {
    Path     string
    Quality  string
    Folder   string
    Filename string
}
```

## Core Functions

### Configuration Loading
```go
// LoadConfig loads and validates the configuration file
func LoadConfig(path string) (*Config, error)

// ValidateConfig ensures all configuration values are valid
func ValidateConfig(config *Config) error
```

### User/Group Operations
```go
// GetUIDGID retrieves numeric UID/GID for user/group names
func GetUIDGID(username, groupname string) (uid, gid int, err error)

// SetFileOwnership sets ownership of a file/directory
func SetFileOwnership(path string, uid, gid int) error
```

### Directory Operations
```go
// CreateDirectory creates a directory with proper permissions
func CreateDirectory(path string, uid, gid int) error

// GetQualityFromPath extracts quality level from path
func GetQualityFromPath(path string, qualityOrder []string) string

// ScanDirectory scans a directory for media files
func ScanDirectory(path string) ([]MediaFile, error)
```

### Media Operations
```go
// MergeMedia performs the media merge operation
func MergeMedia(config *Config) error

// CreateHardLink creates a hard link with proper permissions
func CreateHardLink(source, target string) error
```

## HTTP API

### Routes
```go
// SetupRoutes configures the HTTP routes
func SetupRoutes(router *gin.Engine) {
    router.GET("/media/merge/status", getStatus)
    router.POST("/media/merge", startMerge)
}
```

### Response Types
```go
type StatusResponse struct {
    Status string  `json:"status"`
    Config *Config `json:"config"`
}

type MergeResponse struct {
    Status  string `json:"status"`
    Message string `json:"message"`
}

type ErrorResponse struct {
    Status  string `json:"status"`
    Message string `json:"message"`
}
```

## Implementation Requirements

### Hard Links
- Use `os.Link()` for creating hard links
- Verify source and target are on same filesystem
- Handle existing files by removing before linking

### File System Operations
- Use `os.MkdirAll()` for directory creation
- Set permissions to 0755 for directories
- Preserve original file permissions for hard links
- Handle symlinks appropriately

### Error Handling
- Return appropriate HTTP status codes (400, 500, etc.)
- Log all operations with proper error context
- Implement graceful error recovery
- Return descriptive error messages

### Configuration Validation
- Verify all paths are absolute
- Validate user/group existence
- Check filesystem compatibility for hard links
- Verify quality levels in path names

### Quality Selection Logic
```go
// Example quality selection logic
func selectBestQuality(files []MediaFile, qualityOrder []string) *MediaFile {
    qualityMap := make(map[string]int)
    for i, q := range qualityOrder {
        qualityMap[q] = len(qualityOrder) - i
    }
    
    var best *MediaFile
    bestScore := -1
    
    for _, file := range files {
        if score, ok := qualityMap[file.Quality]; ok && score > bestScore {
            best = &file
            bestScore = score
        }
    }
    
    return best
}
```

## Dependencies
```go
// go.mod
module media-manager

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/spf13/viper v1.18.2
    github.com/sirupsen/logrus v1.9.3
)
```

## Build and Run
```bash
# Build
go build -o media-manager ./cmd/media-manager

# Run
./media-manager --config config.json
```

## Testing
```go
// Example test structure
func TestMergeMedia(t *testing.T) {
    tests := []struct {
        name    string
        config  Config
        wantErr bool
    }{
        {
            name: "basic_merge",
            config: Config{
                User:  "media",
                Group: "media",
                QualityOrder: []string{"4k", "uhd", "hd"},
                Types: map[string]Type{
                    "movies": {
                        SourcePaths: []string{"/media/movies-4k", "/media/movies-hd"},
                        MergedPath: "/media/movies-merged",
                    },
                },
            },
            wantErr: false,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := MergeMedia(&tt.config)
            if (err != nil) != tt.wantErr {
                t.Errorf("MergeMedia() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}
```

## Security Considerations
1. File permissions must be set correctly
2. User input must be validated
3. Paths must be sanitized
4. Error messages must not expose sensitive information
5. API endpoints should be protected if exposed publicly

## Performance Optimization
1. Use goroutines for parallel processing
2. Implement efficient file scanning
3. Cache filesystem operations where appropriate
4. Use buffered channels for file processing
5. Implement proper cleanup of resources

For detailed API documentation and examples, refer to the original `media-merge.md` specification. 