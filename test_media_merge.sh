#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Test the status endpoint
echo "Testing /media/merge/status endpoint..."
curl -X GET http://192.168.10.233:5000/media/merge/status
echo -e "\n"

# Test the merge endpoint
echo "Testing /media/merge endpoint..."
curl -X POST http://192.168.10.233:5000/media/merge
echo -e "\n" 