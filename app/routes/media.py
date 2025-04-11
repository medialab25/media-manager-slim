from flask import Blueprint, jsonify, current_app
import requests
from requests.exceptions import RequestException

bp = Blueprint('media', __name__, url_prefix='/media')

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