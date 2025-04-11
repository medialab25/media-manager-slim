from flask import Blueprint, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'Media Manager API is running'
    })

@bp.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'version': '1.0.0'
    }) 