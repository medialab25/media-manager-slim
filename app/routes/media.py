from flask import Blueprint, jsonify, current_app
import requests
from requests.exceptions import RequestException
import os
import json
from pathlib import Path
import shutil
import grp
import pwd
import logging

bp = Blueprint('media', __name__, url_prefix='/media')

def load_merge_config():
    """Load and validate media merge configuration"""
    try:
        # Get media merge config from app config
        config = current_app.config.get('MEDIA_MERGE')
        if not config:
            raise ValueError("Media merge configuration not found in app config")
            
        # Basic validation
        required_fields = ['user', 'group', 'quality_order', 'types']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
                
        # Validate paths
        for media_type, paths in config['types'].items():
            if 'source_paths' not in paths:
                raise ValueError(f"Missing source_paths for {media_type}")
            if not isinstance(paths['source_paths'], list):
                raise ValueError(f"source_paths for {media_type} must be a list")
            if not paths['source_paths']:
                raise ValueError(f"source_paths for {media_type} cannot be empty")
            if 'merged_path' not in paths:
                raise ValueError(f"Missing merged_path for {media_type}")
                
            # Validate all source paths are absolute
            for source_path in paths['source_paths']:
                if not os.path.isabs(source_path):
                    raise ValueError(f"Source path {source_path} for {media_type} must be absolute")
                    
            # Validate merged path is absolute
            if not os.path.isabs(paths['merged_path']):
                raise ValueError(f"Merged path for {media_type} must be absolute")
                
        return config
    except ValueError as e:
        raise ValueError(str(e))

def get_uid_gid(user, group):
    """Get UID and GID for user and group"""
    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        return uid, gid
    except KeyError as e:
        raise ValueError(f"User or group not found: {str(e)}")

def create_directory(path, uid, gid):
    """Create directory with correct ownership and permissions"""
    print(f"Creating directory: {path}")
    if not os.path.exists(path):
        os.makedirs(path, mode=0o755)
    os.chown(path, uid, gid)
    os.chmod(path, 0o755)
    print(f"Directory created and permissions set: {path}")

def get_quality_from_path(path, quality_order):
    """Extract quality from path name"""
    for quality in quality_order:
        if f"-{quality}" in path:
            return quality
    return None

def merge_media(config):
    """Merge media from source paths to merged path"""
    try:
        print("Starting media merge process...")
        print(f"Config: {json.dumps(config, indent=2)}")
        
        uid, gid = get_uid_gid(config['user'], config['group'])
        print(f"Using UID: {uid}, GID: {gid}")
        
        for media_type, paths in config['types'].items():
            print(f"\nProcessing media type: {media_type}")
            merged_path = paths['merged_path']
            create_directory(merged_path, uid, gid)
            
            # Track processed folders to avoid duplicates
            processed_folders = set()
            
            # Track files that should exist in merged location
            expected_files = set()
            
            # Process source paths in quality order
            for source_path in paths['source_paths']:
                print(f"\nChecking source path: {source_path}")
                quality = get_quality_from_path(source_path, config['quality_order'])
                if not quality:
                    print(f"No quality found in path: {source_path}")
                    continue
                    
                if not os.path.exists(source_path):
                    print(f"Source path does not exist: {source_path}")
                    continue
                    
                print(f"Found quality: {quality}")
                
                # Process each folder in the source path
                for folder in os.listdir(source_path):
                    folder_path = os.path.join(source_path, folder)
                    print(f"\nProcessing folder: {folder_path}")
                    
                    if not os.path.isdir(folder_path):
                        print(f"Not a directory, skipping: {folder_path}")
                        continue
                        
                    # Skip if we've already processed this folder
                    if folder in processed_folders:
                        print(f"Already processed folder: {folder}")
                        continue
                        
                    # Create corresponding folder in merged path
                    merged_folder = os.path.join(merged_path, folder)
                    print(f"Creating merged folder: {merged_folder}")
                    create_directory(merged_folder, uid, gid)
                    
                    # Process all files in the folder
                    for file in os.listdir(folder_path):
                        source_file = os.path.join(folder_path, file)
                        if not os.path.isfile(source_file):
                            print(f"Not a file, skipping: {source_file}")
                            continue
                            
                        # Get base filename without quality suffix
                        base_name = file
                        for q in config['quality_order']:
                            base_name = base_name.replace(f"-{q}", "")
                            
                        # Create hard link in merged folder with quality suffix
                        merged_file = os.path.join(merged_folder, f"{base_name}-{quality}{os.path.splitext(file)[1]}")
                        expected_files.add(merged_file)  # Track expected file
                        print(f"Creating hard link: {source_file} -> {merged_file}")
                        if os.path.exists(merged_file):
                            print(f"Removing existing file: {merged_file}")
                            os.remove(merged_file)
                        os.link(source_file, merged_file)
                        print(f"Hard link created: {merged_file}")
                        
                    processed_folders.add(folder)
                    print(f"Folder processed: {folder}")
            
            # Cleanup: Remove files that no longer exist in source paths
            print("\nStarting cleanup of removed files...")
            for root, _, files in os.walk(merged_path):
                for file in files:
                    merged_file = os.path.join(root, file)
                    if merged_file not in expected_files:
                        print(f"Removing orphaned file: {merged_file}")
                        try:
                            os.remove(merged_file)
                            print(f"Successfully removed: {merged_file}")
                        except Exception as e:
                            print(f"Error removing file {merged_file}: {str(e)}")
            
            # Cleanup: Remove empty directories
            print("\nCleaning up empty directories...")
            for root, dirs, _ in os.walk(merged_path, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):
                            print(f"Removing empty directory: {dir_path}")
                            os.rmdir(dir_path)
                    except Exception as e:
                        print(f"Error removing directory {dir_path}: {str(e)}")
                    
        print("\nMedia merge process completed successfully")
                    
    except Exception as e:
        print(f"Error during merge: {str(e)}")
        raise ValueError(f"Error during merge: {str(e)}")

@bp.route('/refresh', methods=['POST'])
def refresh():
    try:
        # Get JellyFin configuration from app config
        jellyfin_url = current_app.config['JELLYFIN']['URL']
        jellyfin_token = current_app.config['JELLYFIN']['TOKEN']
        
        # Prepare headers for JellyFin API request
        headers = {
            'X-Emby-Token': jellyfin_token,
            'Content-Type': 'application/json'
        }
        
        # Make request to JellyFin API - using query parameters instead of body
        response = requests.post(
            f"{jellyfin_url}/Library/Refresh",
            params={'refreshMode': 'Full'},
            headers=headers
        )
        
        # Check response status
        if response.status_code == 200 or response.status_code == 204:
            return jsonify({
                'status': 'ok',
                'message': 'Successfully refreshed JellyFin libraries'
            })
        elif response.status_code == 401:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JellyFin API token'
            }), 401
        else:
            return jsonify({
                'status': 'error',
                'message': f'JellyFin API error: {response.text}'
            }), 400
            
    except RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to connect to JellyFin server: {str(e)}'
        }), 500
    except KeyError as e:
        return jsonify({
            'status': 'error',
            'message': f'Missing JellyFin configuration: {str(e)}'
        }), 500

@bp.route('/merge/status', methods=['GET'])
def merge_status():
    """Get current status of media merge configuration"""
    try:
        config = load_merge_config()
        return jsonify({
            'status': 'ok',
            'config': {
                'user': config['user'],
                'group': config['group'],
                'quality_order': config['quality_order'],
                'types': {
                    media_type: {
                        'source_paths': paths['source_paths'],
                        'merged_path': paths['merged_path']
                    }
                    for media_type, paths in config['types'].items()
                }
            }
        })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@bp.route('/merge', methods=['POST'])
def merge():
    """Start the media merge process"""
    try:
        config = load_merge_config()
        merge_media(config)
        return jsonify({
            'status': 'ok',
            'message': 'Merge process completed successfully'
        })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400 