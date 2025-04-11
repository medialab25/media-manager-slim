#!/usr/bin/env python3
import os
import shutil
import json
from pathlib import Path

def setup_test_environment():
    """Create test directories and files"""
    # Create base directories
    base_dirs = [
        '/media/tv-hd',
        '/media/tv-uhd',
        '/media/tv-4k',
        '/media/tv-merged',
        '/media/movies-hd',
        '/media/movies-uhd',
        '/media/movies-4k',
        '/media/movies-merged'
    ]
    
    for dir_path in base_dirs:
        os.makedirs(dir_path, exist_ok=True)
        os.chmod(dir_path, 0o755)
        os.chown(dir_path, 1000, 1000)  # media:media
    
    # Create test files
    test_files = {
        'tv-hd': {
            'movie_1': ['film-hd.mkv'],
            'movie_2': ['film-hd.mkv']
        },
        'tv-uhd': {
            'movie_1': ['film-uhd.mkv']
        },
        'movies-hd': {
            'film_1': ['movie-hd.mkv']
        },
        'movies-uhd': {
            'film_1': ['movie-uhd.mkv']
        }
    }
    
    for quality, movies in test_files.items():
        for movie, files in movies.items():
            movie_dir = os.path.join('/media', quality, movie)
            os.makedirs(movie_dir, exist_ok=True)
            os.chmod(movie_dir, 0o755)
            os.chown(movie_dir, 1000, 1000)
            
            for file in files:
                file_path = os.path.join(movie_dir, file)
                with open(file_path, 'w') as f:
                    f.write(f"Content for {file}")
                os.chmod(file_path, 0o644)
                os.chown(file_path, 1000, 1000)

def test_basic_operation():
    """Test basic operation with multiple types"""
    print("\nTesting basic operation with multiple types...")
    from app.routes.media import merge_media
    
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    merge_media(config['MEDIA_MERGE'])
    
    # Verify results
    expected_files = {
        '/media/tv-merged/movie_1/film-uhd.mkv': True,
        '/media/tv-merged/movie_2/film-hd.mkv': True,
        '/media/movies-merged/film_1/movie-uhd.mkv': True
    }
    
    for file_path, should_exist in expected_files.items():
        exists = os.path.exists(file_path)
        print(f"Checking {file_path}: {'✓' if exists == should_exist else '✗'}")
        if exists:
            with open(file_path, 'r') as f:
                print(f"  Content: {f.read()}")

def test_add_uhd_film():
    """Test adding UHD film when HD exists"""
    print("\nTesting adding UHD film when HD exists...")
    # Create HD version
    hd_dir = '/media/tv-hd/movie_1'
    os.makedirs(hd_dir, exist_ok=True)
    hd_file = os.path.join(hd_dir, 'film-hd.mkv')
    with open(hd_file, 'w') as f:
        f.write("HD content")
    
    # Create UHD version
    uhd_dir = '/media/tv-uhd/movie_1'
    os.makedirs(uhd_dir, exist_ok=True)
    uhd_file = os.path.join(uhd_dir, 'film-uhd.mkv')
    with open(uhd_file, 'w') as f:
        f.write("UHD content")
    
    # Run merge
    from app.routes.media import merge_media
    with open('config.json', 'r') as f:
        config = json.load(f)
    merge_media(config['MEDIA_MERGE'])
    
    # Verify UHD version is used
    merged_file = '/media/tv-merged/movie_1/film-uhd.mkv'
    exists = os.path.exists(merged_file)
    print(f"Checking {merged_file}: {'✓' if exists else '✗'}")
    if exists:
        with open(merged_file, 'r') as f:
            print(f"  Content: {f.read()}")

def test_add_hd_film():
    """Test adding HD film when no UHD exists"""
    print("\nTesting adding HD film when no UHD exists...")
    # Create HD version
    hd_dir = '/media/tv-hd/movie_1'
    os.makedirs(hd_dir, exist_ok=True)
    hd_file = os.path.join(hd_dir, 'film-hd.mkv')
    with open(hd_file, 'w') as f:
        f.write("HD content")
    
    # Run merge
    from app.routes.media import merge_media
    with open('config.json', 'r') as f:
        config = json.load(f)
    merge_media(config['MEDIA_MERGE'])
    
    # Verify HD version is used
    merged_file = '/media/tv-merged/movie_1/film-hd.mkv'
    exists = os.path.exists(merged_file)
    print(f"Checking {merged_file}: {'✓' if exists else '✗'}")
    if exists:
        with open(merged_file, 'r') as f:
            print(f"  Content: {f.read()}")

def test_remove_uhd_film():
    """Test removing UHD film when HD exists"""
    print("\nTesting removing UHD film when HD exists...")
    # Remove UHD version
    uhd_file = '/media/tv-uhd/movie_1/film-uhd.mkv'
    if os.path.exists(uhd_file):
        os.remove(uhd_file)
    
    # Run merge
    from app.routes.media import merge_media
    with open('config.json', 'r') as f:
        config = json.load(f)
    merge_media(config['MEDIA_MERGE'])
    
    # Verify HD version is used
    merged_file = '/media/tv-merged/movie_1/film-hd.mkv'
    exists = os.path.exists(merged_file)
    print(f"Checking {merged_file}: {'✓' if exists else '✗'}")
    if exists:
        with open(merged_file, 'r') as f:
            print(f"  Content: {f.read()}")

def test_remove_uhd_film_no_hd():
    """Test removing UHD film when no HD exists"""
    print("\nTesting removing UHD film when no HD exists...")
    # Remove UHD version
    uhd_file = '/media/tv-uhd/movie_1/film-uhd.mkv'
    if os.path.exists(uhd_file):
        os.remove(uhd_file)
    
    # Remove HD version
    hd_file = '/media/tv-hd/movie_1/film-hd.mkv'
    if os.path.exists(hd_file):
        os.remove(hd_file)
    
    # Run merge
    from app.routes.media import merge_media
    with open('config.json', 'r') as f:
        config = json.load(f)
    merge_media(config['MEDIA_MERGE'])
    
    # Verify merged directory is empty
    merged_dir = '/media/tv-merged/movie_1'
    exists = os.path.exists(merged_dir)
    print(f"Checking {merged_dir}: {'✓' if exists else '✗'}")
    if exists:
        files = os.listdir(merged_dir)
        print(f"  Files in directory: {files}")

def test_uhd_only():
    """Test having UHD but not HD"""
    print("\nTesting having UHD but not HD...")
    # Create UHD version
    uhd_dir = '/media/tv-uhd/movie_1'
    os.makedirs(uhd_dir, exist_ok=True)
    uhd_file = os.path.join(uhd_dir, 'film-uhd.mkv')
    with open(uhd_file, 'w') as f:
        f.write("UHD content")
    
    # Run merge
    from app.routes.media import merge_media
    with open('config.json', 'r') as f:
        config = json.load(f)
    merge_media(config['MEDIA_MERGE'])
    
    # Verify UHD version is used
    merged_file = '/media/tv-merged/movie_1/film-uhd.mkv'
    exists = os.path.exists(merged_file)
    print(f"Checking {merged_file}: {'✓' if exists else '✗'}")
    if exists:
        with open(merged_file, 'r') as f:
            print(f"  Content: {f.read()}")

if __name__ == '__main__':
    print("Setting up test environment...")
    setup_test_environment()
    
    print("\nRunning all tests...")
    test_basic_operation()
    test_add_uhd_film()
    test_add_hd_film()
    test_remove_uhd_film()
    test_remove_uhd_film_no_hd()
    test_uhd_only()
    
    print("\nAll tests completed!") 